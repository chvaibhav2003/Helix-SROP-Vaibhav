import re
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings as ChromaSettings  # ✅ FIXED
from app.settings import settings
import hashlib
import argparse
import asyncio

def chunk_markdown(text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
    """
    Heading-aware chunking with fallback splitting just normal algo for large sections

    also added the split heading 
    """

    # 🔹 Step 1: Split by headings
    sections = re.split(r"(?=\n## |\n### )", text)

    chunks = []

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # 🔹 Step 2: If section is small → keep as is
        if len(section) <= chunk_size:
            chunks.append(section)
        else:
            # 🔹 Step 3: Fallback splitting (sliding window)
            start = 0
            while start < len(section):
                end = start + chunk_size
                chunk = section[start:end]
                chunks.append(chunk)

                # 🔹 Step 4: Move with overlap
                start += chunk_size - overlap

    return chunks



def extract_metadata(file_path: Path, text: str) -> dict:
    """
    Extract metadata from markdown frontmatter.

    Example frontmatter:
    ---
    title: Deploy Keys
    product_area: security
    tags: [keys, secrets]
    ---
    """

    metadata = {
        "source": file_path.name,
    }

    # 🔹 Find frontmatter block
    match = re.search(r"^---\n(.*?)\n---", text, re.DOTALL)

    if not match:
        return metadata

    frontmatter = match.group(1)

    # 🔹 Extract key-value pairs
    for line in frontmatter.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()

    return metadata


async def ingest_directory(docs_path: Path, chunk_size: int, chunk_overlap: int) -> None:
    md_files = list(docs_path.rglob("*.md"))
    print(f"Found {len(md_files)} markdown files in {docs_path}")

    # 🔹 Init embedding model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # 🔹 Init Chroma client
    client = chromadb.PersistentClient(
    path=settings.chroma_persist_dir
)

    collection = client.get_or_create_collection(name="helix_docs")

    for file_path in md_files:
        text = file_path.read_text(encoding="utf-8")

        metadata = extract_metadata(file_path, text)
        chunks = chunk_markdown(text, chunk_size, chunk_overlap)

        print(f"  {file_path.name}: {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            # 🔹 Stable chunk ID
            chunk_id = hashlib.sha256(
                f"{file_path.name}_{i}".encode()
            ).hexdigest()

            embedding = model.encode(chunk).tolist()

            collection.upsert(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[metadata],
            )

    
    print("Ingest complete.")

def main():
    parser = argparse.ArgumentParser(description="Ingest docs into vector store")
    parser.add_argument("--path", type=Path, required=True)
    parser.add_argument("--chunk-size", type=int, default=512)
    parser.add_argument("--chunk-overlap", type=int, default=64)

    args = parser.parse_args()

    asyncio.run(
        ingest_directory(args.path, args.chunk_size, args.chunk_overlap)
    )


if __name__ == "__main__":
    main()