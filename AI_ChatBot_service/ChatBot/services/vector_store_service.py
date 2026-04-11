# ChatBot/services/vector_store_service.py

from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)


class VectorStoreService:
    COLLECTION_NAME = "chatbot_lecture_chunks"
    VECTOR_DIM = 1024  # bge-m3
    METRIC_TYPE = "COSINE"

    def __init__(self, host="localhost", port="19530"):
        self.host = host
        self.port = port
        self.collection_name = self.COLLECTION_NAME

    def connect(self):
        connections.connect(
            alias="default",
            host=self.host,
            port=self.port,
        )

    def create_collection_if_not_exists(self):
        if utility.has_collection(self.collection_name):
            return Collection(self.collection_name)

        fields = [
            FieldSchema(
                name="chunk_id",
                dtype=DataType.VARCHAR,
                is_primary=True,
                auto_id=False,
                max_length=64,
            ),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=self.VECTOR_DIM,
            ),
            FieldSchema(
                name="chunk_text",
                dtype=DataType.VARCHAR,
                max_length=65535,
            ),
            FieldSchema(
                name="lecture_id",
                dtype=DataType.VARCHAR,
                max_length=64,
            ),
            FieldSchema(
                name="course_id",
                dtype=DataType.VARCHAR,
                max_length=64,
            ),
            FieldSchema(
                name="student_id",
                dtype=DataType.VARCHAR,
                max_length=64,
            ),
            FieldSchema(
                name="chunk_index",
                dtype=DataType.INT64,
            ),
            FieldSchema(
                name="source_type",
                dtype=DataType.VARCHAR,
                max_length=32,
            ),
            FieldSchema(
                name="created_at",
                dtype=DataType.INT64,
            ),
        ]

        schema = CollectionSchema(
            fields=fields,
            description="Lecture chunks for Moein chatbot RAG",
        )

        return Collection(
            name=self.collection_name,
            schema=schema,
        )

    def create_index(self):
        collection = Collection(self.collection_name)

        index_params = {
            "metric_type": self.METRIC_TYPE,
            "index_type": "AUTOINDEX",
            "params": {},
        }

        collection.create_index(
            field_name="embedding",
            index_params=index_params,
        )

    def load_collection(self):
        collection = Collection(self.collection_name)
        collection.load()

    def setup(self):
        self.connect()
        self.create_collection_if_not_exists()
        self.create_index()
        self.load_collection()

    def insert_chunk(
        self,
        chunk_id: str,
        embedding: list[float],
        chunk_text: str,
        lecture_id: str,
        course_id: str,
        student_id: str,
        chunk_index: int,
        source_type: str,
        created_at: int,
    ):
        collection = Collection(self.collection_name)

        data = [
            [chunk_id],
            [embedding],
            [chunk_text],
            [lecture_id],
            [course_id],
            [student_id],
            [chunk_index],
            [source_type],
            [created_at],
        ]

        collection.insert(data)
        collection.flush()

    def search_chunks(
        self,
        query_embedding: list[float],
        limit: int = 5,
        student_id: str | None = None,
        course_id: str | None = None,
        lecture_id: str | None = None,
    ):
        collection = Collection(self.collection_name)

        filters = []
        if student_id:
            filters.append(f'student_id == "{student_id}"')
        if course_id:
            filters.append(f'course_id == "{course_id}"')
        if lecture_id:
            filters.append(f'lecture_id == "{lecture_id}"')

        expr = " and ".join(filters) if filters else None

        results = collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param={
                "metric_type": self.METRIC_TYPE,
                "params": {},
            },
            limit=limit,
            expr=expr,
            output_fields=[
                "chunk_text",
                "lecture_id",
                "course_id",
                "chunk_index",
                "source_type",
                "student_id",
            ],
        )

        normalized_results = []

        for hits in results:
            for hit in hits:
                normalized_results.append(
                    {
                        "chunk_id": hit.id,
                        "chunk_text": hit.entity.get("chunk_text"),
                        "lecture_id": hit.entity.get("lecture_id"),
                        "course_id": hit.entity.get("course_id"),
                        "chunk_index": hit.entity.get("chunk_index"),
                        "source_type": hit.entity.get("source_type"),
                        "student_id": hit.entity.get("student_id"),
                        "score": hit.distance,
                    }
                )

        return normalized_results