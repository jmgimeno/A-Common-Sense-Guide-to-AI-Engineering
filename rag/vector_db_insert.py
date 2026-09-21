import os
from dotenv import load_dotenv
from pinecone import Pinecone
import re

load_dotenv()


def split_markdown_by_h1(md_text):
    """Converts Markdown file into a list of text chunks.
    Each chunk spans one section of the text, defined by H1s"""
    pattern = r"(?m)^# .+?(?=^# |\Z)"  # from an H1 to the next H1 or EOF
    chunks = re.findall(pattern, md_text, re.DOTALL)
    return [chunk.strip() for chunk in chunks if chunk.strip()]

# Convert the Flamehamster manual into list of chunks:
with open("flamehamster.md", "r", encoding="utf-8") as f:
    md_content = f.read()

chunks = split_markdown_by_h1(md_content)

# Wrap each chunk in the record format that Pinecone wants:
records = []
for i, chunk in enumerate(chunks):
    records.append({
        "id": f"chunk-{i}",
        "chunk_text": chunk,
        "manual": "flamehamster"
    })

# Insert records into Pinecone: (Pinecone will create the chunk
# embeddings automatically.)
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
dense_index = pc.Index("gross-app")

dense_index.upsert_records("flamehamster", records)
