"""Charge et indexe les données Markdown dans Upstash Vector"""
import os
from pathlib import Path
from dotenv import load_dotenv
from upstash_vector import Index, Vector
import re

load_dotenv()

def chunk_markdown(content: str) -> list[str]:
    sections = re.split(r'(^## .+$)', content, flags=re.MULTILINE)
    chunks = []
    
    for i in range(0, len(sections), 2):
        if i < len(sections):
            title = sections[i].strip()
            content_part = sections[i + 1].strip() if i + 1 < len(sections) else ""
            chunk = f"{title}\n{content_part}" if title and content_part else (title or content_part)
            
            if chunk.strip() and len(chunk.strip()) > 10:
                chunks.append(chunk.strip())
    
    return chunks if chunks else [content.strip()]

idx = Index(url=os.getenv("UPSTASH_VECTOR_REST_URL"), token=os.getenv("UPSTASH_VECTOR_REST_TOKEN"))

vectors = []
for md_file in Path("data").glob("*.md"):
    content = md_file.read_text(encoding="utf-8")
    for i, chunk in enumerate(chunk_markdown(content)):
        vectors.append(Vector(
            id=f"{md_file.stem}-{i}",
            data=chunk,
            metadata={"source": md_file.stem}
        ))

for i in range(0, len(vectors), 100):
    idx.upsert(vectors=vectors[i:i + 100])

print(f" {len(vectors)} chunks indexés")
