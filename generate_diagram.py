import base64
import json
import urllib.request
import urllib.parse

def create_mermaid_jpeg():
    mermaid_code = """graph TD
    A[(PostgreSQL DB<br/>'aiims_guidelines')] -->|Fetch Text Chunks| B(ETL Pipeline<br/>build_knowledge_graph.py)
    B -->|Send Text Chunks| C[Gemini LLM<br/>gemini-2.5-flash]
    C -->|Extract Entities & Relationships| D{Structured Data:<br/>Diseases, Drugs,<br/>Symptoms, Conditions}
    D -->|Ingest via Concurrent Cypher Queries| E[(Neo4j DB<br/>Knowledge Graph)]
    
    subgraph Neo4j Schema Schema
        F((GuidelineChunk))
        G((Disease))
        H((Drug))
        I((Symptom))
        J((Condition))
        F -.->|MENTIONS| G
        F -.->|MENTIONS| H
        F -.->|MENTIONS| I
        F -.->|MENTIONS| J
        G -.->|TREATED_BY| H
        G -.->|HAS_SYMPTOM| I
        H -.->|CONTRAINDICATED_IN| J
        H -.->|CAUSES_SIDE_EFFECT| I
        H -.->|INTERACTS_WITH| H
    end
    E --- F
    """

    # Encode mermaid code to base64
    graphbytes = mermaid_code.encode("ascii")
    base64_bytes = base64.b64encode(graphbytes)
    base64_string = base64_bytes.decode("ascii")

    # Create URL for mermaid.ink
    # It returns a PNG image by default
    url = f"https://mermaid.ink/img/{base64_string}?bgColor=white"

    try:
        # We will download the image and save it. 
        # Using pure python standard library to avoid external dependencies (except for Pillow if needed for PNG->JPEG, but we can try to save it as JPEG directly using Pillow if available, otherwise just save as PNG and rename/warn)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            image_data = response.read()

        # If Pillow is installed, convert PNG to JPEG
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(image_data))
            rgb_img = img.convert('RGB')
            output_file = "architecture_diagram.jpeg"
            rgb_img.save(output_file, "JPEG")
            print(f"Successfully generated and saved as {output_file} (using Pillow for JPEG conversion)")
        except ImportError:
            # Fallback if Pillow is not installed: just save the PNG data but name it jpg (not ideal but works for some viewers), 
            # or better yet, save as PNG and tell the user.
            output_file = "architecture_diagram.png"
            with open(output_file, "wb") as f:
                f.write(image_data)
            print("Pillow (PIL) is not installed. Saved as PNG instead:", output_file)
            print("To save as actual JPEG, please run: pip install Pillow")

    except Exception as e:
        print(f"Failed to generate diagram: {e}")

if __name__ == "__main__":
    create_mermaid_jpeg()
