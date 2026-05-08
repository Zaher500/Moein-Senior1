import os #  embedding : convert text to vector ... bgm3: convert text to embdding 
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()
from typing import List



class EmbeddingService:   #ZZ4
    MODEL_NAME = "BAAI/bge-m3"
    EXPECTED_DIMENSION = 1024

    _model = None

    @classmethod
    def _get_model(cls) -> SentenceTransformer:
        if cls._model is None:
            cls._model = SentenceTransformer(
                cls.MODEL_NAME,
                token=os.getenv("HF_TOKEN"),   
                )
        return cls._model

    @classmethod
    def embed_text(cls, text: str) -> List[float]:       # عم يعمل امبدنغ  وبيرجع الاستجابة للراغ سيرفس
        if not text or not text.strip():
            raise ValueError("Text for embedding cannot be empty.")

        model = cls._get_model()
        embedding = model.encode(
            text,
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).tolist()

        cls._validate_embedding_dimension(embedding)
        return embedding                         #  وبيرجع الاستجابة للراغ سيرف هلق منروح عالراغ

    @classmethod
    def embed_texts(cls, texts: List[str]) -> List[List[float]]:
        if not texts:
            raise ValueError("Texts list for embedding cannot be empty.")

        cleaned_texts = []
        for text in texts:
            if not text or not text.strip():
                raise ValueError("Texts list contains an empty text.")
            cleaned_texts.append(text)

        model = cls._get_model()
        embeddings = model.encode(
            cleaned_texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).tolist()

        for embedding in embeddings:
            cls._validate_embedding_dimension(embedding)

        return embeddings

    @classmethod
    def _validate_embedding_dimension(cls, embedding: List[float]) -> None:
        if len(embedding) != cls.EXPECTED_DIMENSION:
            raise ValueError(
                f"Invalid embedding dimension: expected {cls.EXPECTED_DIMENSION}, got {len(embedding)}"
            )