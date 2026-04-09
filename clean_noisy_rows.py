"""
One-time cleanup script: Removes noisy/administrative rows from aiims_guidelines.
Run this once to clean existing data. Future ingestions will prevent noise via db_setup.py.

Usage: python clean_noisy_rows.py
"""
import psycopg2
import os
import sys
from dotenv import load_dotenv

load_dotenv()

PG_URI = os.getenv("PG_URI", "postgresql://postgres:mysecretpassword@localhost:5432/postgres")

# Keywords that indicate non-clinical, administrative content
NOISE_KEYWORDS = [
    "standard treatment guidelines",
    "first edition",
    "second edition",
    "message from",
    "preface",
    "foreword",
    "acknowledgement",
    "acknowledgment",
    "table of contents",
    "contents",
    "index",
    "copyright",
    "all rights reserved",
    "disclaimer",
    "published by",
    "printing",
    "isbn",
    "contributors",
    "committee",
    "abbreviations used",
    "list of abbreviations",
]

MIN_CHUNK_WORDS = 30  # Chunks shorter than this are likely headers/page numbers


def clean_noisy_rows():
    """Deletes noisy administrative rows from aiims_guidelines."""
    conn = psycopg2.connect(PG_URI)
    conn.autocommit = True
    cursor = conn.cursor()

    # Get initial count
    cursor.execute("SELECT COUNT(*) FROM aiims_guidelines")
    initial_count = cursor.fetchone()[0]
    print(f"Initial row count: {initial_count}")

    # Step 1: Delete very short chunks (< MIN_CHUNK_WORDS words)
    cursor.execute("""
        DELETE FROM aiims_guidelines 
        WHERE array_length(string_to_array(trim(content), ' '), 1) < %s
        RETURNING id
    """, (MIN_CHUNK_WORDS,))
    short_deleted = cursor.rowcount
    print(f"Deleted {short_deleted} short chunks (< {MIN_CHUNK_WORDS} words)")

    # Step 2: Delete chunks containing noise keywords (only if chunk is relatively short — avoid deleting
    # genuine clinical content that merely mentions "contents" in passing)
    total_keyword_deleted = 0
    for keyword in NOISE_KEYWORDS:
        cursor.execute("""
            DELETE FROM aiims_guidelines 
            WHERE LOWER(content) LIKE %s 
              AND array_length(string_to_array(trim(content), ' '), 1) < 80
            RETURNING id
        """, (f"%{keyword}%",))
        count = cursor.rowcount
        if count > 0:
            total_keyword_deleted += count
            print(f"  Deleted {count} rows matching '{keyword}'")

    # Get final count
    cursor.execute("SELECT COUNT(*) FROM aiims_guidelines")
    final_count = cursor.fetchone()[0]

    print(f"\n{'='*50}")
    print(f"Cleanup Complete!")
    print(f"  Before: {initial_count} rows")
    print(f"  Removed: {initial_count - final_count} rows")
    print(f"    - Short chunks: {short_deleted}")
    print(f"    - Noise keywords: {total_keyword_deleted}")
    print(f"  After:  {final_count} rows")
    print(f"{'='*50}")

    conn.close()


if __name__ == "__main__":
    clean_noisy_rows()
