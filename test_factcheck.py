from pipeline.refine import find_factual_issues, apply_corrections

source = open("sources/vector_databases.txt", encoding="utf-8").read()

bad_draft = """# Vector Databases Explained

## How Search Works

Vector databases find results by matching the exact keywords in your query against stored text, which is why they cannot handle synonyms. To keep searches fast, they rely on HNSW, an algorithm that guarantees perfectly exact results with no loss of accuracy at all.

## Popular Tools

Popular options include Pinecone, Weaviate, Milvus, Qdrant, and Chroma. PostgreSQL cannot store vectors in any form, so teams must always use a dedicated database.
"""

print("=== BEFORE ===")
print(bad_draft)
issues = find_factual_issues(bad_draft, source)
print("=== ISSUES FOUND ===")
for i in issues:
    print("-", i["claim"], "=>", i["correction"])
fixed = apply_corrections(bad_draft, issues) if issues else bad_draft
print("\n=== AFTER ===")
print(fixed)
