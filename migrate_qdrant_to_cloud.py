"""
One-time migration script: copies local Qdrant collection to Qdrant Cloud.
Run once after setting QDRANT_URL and QDRANT_API_KEY in .env
Usage: python migrate_qdrant_to_cloud.py
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, SparseVectorParams, SparseIndexParams, PointStruct

load_dotenv()

COLLECTION_NAME = "chapter_vi_a_langchain"
APP_ROOT = Path(__file__).resolve().parent
PERSIST_DIR = str(APP_ROOT / "app" / "qdrant_storage")

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if not QDRANT_URL or not QDRANT_API_KEY:
    print("❌ QDRANT_URL and QDRANT_API_KEY must be set in .env")
    exit(1)

print(f"📂 Local storage: {PERSIST_DIR}")
print(f"☁️  Cloud target: {QDRANT_URL}")

# Connect to local Qdrant
local = QdrantClient(path=PERSIST_DIR)

# Connect to Qdrant Cloud
cloud = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# Check if collection exists locally
collections = [c.name for c in local.get_collections().collections]
if COLLECTION_NAME not in collections:
    print(f"❌ Collection '{COLLECTION_NAME}' not found locally. Available: {collections}")
    exit(1)

# Get local collection info
info = local.get_collection(COLLECTION_NAME)
print(f"✅ Found local collection: {COLLECTION_NAME}")
print(f"   Points: {info.points_count}")
print(f"   Vectors config: {info.config.params.vectors}")

# Create collection on cloud if it doesn't exist
cloud_collections = [c.name for c in cloud.get_collections().collections]
if COLLECTION_NAME not in cloud_collections:
    print(f"Creating collection on cloud...")
    # Re-create with same config
    cloud.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=info.config.params.vectors,
        sparse_vectors_config=info.config.params.sparse_vectors,
    )
    print(f"✅ Collection created on cloud")
else:
    print(f"ℹ️  Collection already exists on cloud, will upsert points")

# Migrate points in batches
BATCH_SIZE = 20
offset = None
total_migrated = 0

print(f"\nMigrating points in batches of {BATCH_SIZE}...")

while True:
    # Scroll through local points
    result, next_offset = local.scroll(
        collection_name=COLLECTION_NAME,
        limit=BATCH_SIZE,
        offset=offset,
        with_payload=True,
        with_vectors=True,
    )

    if not result:
        break

    # Convert Record objects to PointStruct
    points_to_upsert = [
        PointStruct(id=r.id, vector=r.vector, payload=r.payload)
        for r in result
    ]

    # Upload to cloud
    cloud.upsert(
        collection_name=COLLECTION_NAME,
        points=points_to_upsert,
    )

    total_migrated += len(result)
    print(f"  Migrated {total_migrated} points...", end="\r")

    if next_offset is None:
        break
    offset = next_offset

print(f"\n✅ Migration complete! {total_migrated} points uploaded to Qdrant Cloud")

# Verify
cloud_info = cloud.get_collection(COLLECTION_NAME)
print(f"☁️  Cloud collection now has {cloud_info.points_count} points")
