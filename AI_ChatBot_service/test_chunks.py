from pymilvus import connections, Collection

connections.connect(alias="default", host="localhost", port="19530")

collection = Collection("chatbot_lecture_chunks")
collection.load()

rows = collection.query(
    expr='student_id == "057a2b90-e8db-4adf-a6e2-135d859c3564"',
    output_fields=[
        "lecture_id",
        "chunk_index",
        "chunk_text",
    ],
)

rows = sorted(rows, key=lambda x: (x["lecture_id"], x["chunk_index"]))

current_lecture = None

for row in rows:
    if row["lecture_id"] != current_lecture:
        current_lecture = row["lecture_id"]
        print(f"\n=== lecture_id: {current_lecture} ===")

    print(f"chunk_{row['chunk_index']}: {row['chunk_text'][:150]}")

    