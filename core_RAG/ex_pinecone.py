import os
import pinecone
from pinecone import ServerlessSpec
from dotenv import load_dotenv


load_dotenv()


index_name = os.getenv("PINECONE_INDEX_NAME")

pc = pinecone.Pinecone(
    api_key=os.environ.get("PINECONE_API_KEY")
)

# Create Index if it doesn't exist
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric='euclidean',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )

index = pc.Index(index_name)
print(f"Connected to Pinecone index: {index_name}")
print(f"Index object: {index.describe_index_stats()}")

# Upsert vectors with metadata
vectors_to_upsert = [
    {
        "id": "doc-1",
        "values": [0.1, 0.2, 0.3, 0.4] + [0.0] * 1532,  # 1536 dimensions
        "metadata": {
            "source": "document_1.pdf",
            "page": 1,
            "text": "Sample document content",
            "author": "John Doe",
            "allowed_users_group": ["user1", "user2"],
            "access_level": "internal"
        }
    },
    {
        "id": "doc-2",
        "values": [0.2, 0.3, 0.4, 0.5] + [0.0] * 1532,  # 1536 dimensions
        "metadata": {
            "source": "document_2.pdf",
            "page": 1,
            "text": "Another document content",
            "author": "Jane Smith",
            "allowed_users_group": ["user3", "user4"],
            "access_level": "public"
        }
    }
]

# # Upsert vectors with metadata
# print("\nUpserting vectors with metadata...")
# index.upsert(vectors=vectors_to_upsert)
# print("✓ Successfully upserted vectors")

# Verify by querying
query_vector = [0.1, 0.2, 0.3, 0.4] + [0.0] * 1532
results = index.query(vector=query_vector, top_k=2, include_metadata=True,
                      filter={"access_level": {"$eq": "internal", "$ne": "public"}})
print(f"\nQuery results: {results.matches}")

"""
$eq: Equal to (number, string)
$ne: Not equal to (number, string)
$gt: Greater than (number)
$lt: Less than (number)
$gte: Greater than or equal to (number)
$lte: Less than or equal to (number)
$in: In Array (string)
$nin: Not in Array (string)
"""

