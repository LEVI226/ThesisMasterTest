import httpx
import json
import time

BASE_URL = "http://localhost:8900"

def test_ocr():
    print("=== Testing OCR Ingestion ===")
    with open("tests/ocr_test.png", "rb") as f:
        files = {"file": ("ocr_test.png", f, "image/png")}
        try:
            resp = httpx.post(f"{BASE_URL}/ocr", files=files, timeout=60.0)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"Ingested: {data.get('ingested_to_rag')}")
                print(f"Text snippet: {repr(data.get('full_text', '')[:100])}")
                return True
            else:
                print(f"Error: {resp.text}")
        except Exception as e:
            print(f"Connection error: {e}")
    return False

def test_rag():
    print("\n=== Testing RAG Q&A ===")
    payload = {
        "question": "What are the two topics covered by the platform report?",
        "language": "en"
    }
    try:
        resp = httpx.post(f"{BASE_URL}/ask", json=payload, timeout=60.0)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Answer: {data.get('answer')}")
            print(f"Sources: {[s.get('filename') for s in data.get('sources', [])]}")
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    if test_ocr():
        # Small delay to ensure ChromaDB indexing if async (though it's sync in current code)
        time.sleep(1)
        test_rag()
