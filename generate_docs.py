#!/usr/bin/env python3
import os
import sys
from pymongo import MongoClient
from collections import defaultdict

# Lee la URI desde la env
MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    print("❌ Error: La variable de entorno MONGODB_URI no está definida", file=sys.stderr)
    sys.exit(1)

DB_NAME = MONGO_URI.rsplit("/", 1)[-1]

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

MAX_SAMPLES = 100

def flatten(doc, parent="", sep="."):
    items = {}
    for k, v in doc.items():
        nk = f"{parent}{sep}{k}" if parent else k
        if isinstance(v, dict):
            items.update(flatten(v, nk, sep))
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            items.update(flatten(v[0], nk + "[0]", sep))
        else:
            items[nk] = type(v).__name__
    return items

def analyze(col):
    fields = defaultdict(set)
    count = 0
    for doc in db[col].find().limit(MAX_SAMPLES):
        for k, t in flatten(doc).items():
            fields[k].add(t)
        count += 1
    return {
        "col": col,
        "sampled": count,
        "estimated": db[col].estimated_document_count(),
        "fields": {k: sorted(v) for k, v in fields.items()}
    }

schema = [analyze(c) for c in db.list_collection_names()]

# Markdown output
os.makedirs("docs", exist_ok=True)
with open("docs/mongodb_schema.md", "w", encoding="utf-8") as f:
    f.write(f"# MongoDB Schema: `{DB_NAME}`\n\n")
    for s in schema:
        f.write(f"## 🗂 `{s['col']}`\n")
        f.write(f"- Estimated: {s['estimated']} docs\n")
        f.write(f"- Sampled: {s['sampled']} docs\n")
        f.write("### Fields:\n")
        for fld, types in s["fields"].items():
            f.write(f"- `{fld}`: {', '.join(types)}\n")
        f.write("\n")
print("✅ docs/mongodb_schema.md generated")
