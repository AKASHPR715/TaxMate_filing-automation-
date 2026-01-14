
import chromadb
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
CHROMA_PATH = BASE_DIR / "app/chroma_db"

print(f"Checking Chroma at {CHROMA_PATH}")

try:
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    colls = client.list_collections()
    print(f"Found {len(colls)} collections:")
    for c in colls:
        print(f" - {c.name} (Count: {c.count()})")
        
except Exception as e:
    print(f"Chroma check failed: {e}")

