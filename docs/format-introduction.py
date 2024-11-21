# Read and concatenate introductions from docs 1-4
docs = [
    "1-function-calling-with-weaviate.md",
    "2-synthetic-database-schemas.md", 
    "3-synthetic-weaviate-queries.md",
    "4-ast-evaluation.md"
]

intro_text = ""
for doc in docs:
    with open(doc, 'r') as f:
        content = f.read()
        # Find text between ## Introduction and next heading
        intro_start = content.find("## Introduction")
        if intro_start != -1:
            intro_start = content.find("\n", intro_start) + 1
            next_heading = content.find("##", intro_start)
            intro_end = next_heading if next_heading != -1 else len(content)
            intro_text += content[intro_start:intro_end].strip() + "\n\n"

print(intro_text)