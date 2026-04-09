import os
from dotenv import load_dotenv
import requests

load_dotenv()

def test_serper():
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        print("\n--- Testing SERPER_API_KEY ---")
        print("Skipping SERPER_API_KEY (not set)")
        return

    print(f"\n--- Testing SERPER_API_KEY ---")
    print(f"API Key (prefix): {api_key[:10]}...")
    
    url = "https://google.serper.dev/search"
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    payload = {
        "q": "medication interactions overview",
        "num": 1
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            if "organic" in data and len(data["organic"]) > 0:
                print(f"SUCCESS! Serper returned results.")
                item = data["organic"][0]
                print(f"Title: {item.get('title')}")
            else:
                print(f"Serper called successfully, but no results found.")
        else:
            print(f"FAILED with status code {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

def test_google_custom_search():
    keys_to_test = {
        "GOOGLE_SEARCH_API_KEY": os.getenv("GOOGLE_SEARCH_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY")
    }
    cx = os.getenv("GOOGLE_SEARCH_CX")
    
    if not cx:
        print("\n--- Testing Google Custom Search ---")
        print("ERROR: GOOGLE_SEARCH_CX not found in .env")
    else:
        for name, api_key in keys_to_test.items():
            if not api_key:
                print(f"\n--- Testing {name} ---")
                print(f"Skipping {name} (not set)")
                continue
                
            print(f"\n--- Testing {name} ---")
            print(f"API Key (prefix): {api_key[:10]}...")
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": api_key,
                "cx": cx,
                "q": "medication interactions overview",
                "num": 1
            }
            
            try:
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if "items" in data:
                        print(f"SUCCESS! {name} returned results.")
                        item = data["items"][0]
                        print(f"Title: {item.get('title')}")
                    else:
                        print(f"API called successfully, but no results found.")
                else:
                    print(f"FAILED with status code {response.status_code}")
                    error_msg = response.json().get("error", {}).get("message", "Unknown error")
                    print(f"Error: {error_msg}")
                    if "does not have the access to Custom Search JSON API" in error_msg:
                        print("NOTE: This usually means the API is discontinued for new projects. Use Serper instead.")
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    print("--- API VERIFICATION SCRIPT ---")
    test_serper()
    test_google_custom_search()

