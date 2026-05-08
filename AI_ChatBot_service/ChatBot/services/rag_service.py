from ChatBot.services.embedding_service import EmbeddingService # chat_orchestrator  بتستلم السؤال من الطالب وبتعمله امبدنغ وبجيب الشانك بلب انعملها امبدنغ وبدين بيبعتهم لل   
from ChatBot.services.vector_store_service import VectorStoreService# هو طلبهم chat_orchestrator لانو ال  
# وبالاخير رحعله الامبدنغvector_store_service مشان يعمل امبدنغ واستعملوا ال  embedding_service هاد بيبغت لل 
# الراغ بيبني الاجابة وبرجها للاوركستريتر
class RAGService:    #ZZ3
    @staticmethod
    def retrieve_context(
        student_id: str,
        query: str,
        course_id: str | None = None,
        lecture_id: str | None = None,
        top_k: int = 5,
        session=None,
    ):
        if not student_id:
            raise ValueError("student_id is required.")

        if not query or not query.strip():
            return {
                "chunks": [],
                "context_text": "",
                "sources": [],
            }
         #ZZ3
        query_embedding = EmbeddingService.embed_text(query)  # عم يبعت التكست للامبدنغ سيؤس
                                                              #هون query_embedding يعني راح عمل الخطوة الرابعة ورجع وخزن الامبدينع 
        vector_store = VectorStoreService()# اتصال مع الفيكتور تاتابز
        vector_store.setup()

        chunks = vector_store.search_chunks(      #ZZ5
            query_embedding=query_embedding,  #USER query embedding عم جيب امحتوى المشابه لل 
            limit=top_k,                      #chunks الخطوة ستة عم نعمل هاد الشي وتخزنوا بال 
            student_id=student_id,
            course_id=course_id,
            lecture_id=lecture_id,
        )

        sorted_chunks = sorted(chunks, key=lambda chunk: chunk["chunk_index"])    # zz7  عم يبعت تريتب الشاتكس حسب موقعهم بالمحاضرة 

        context_text = "\n\n".join(
            chunk["chunk_text"] for chunk in sorted_chunks if chunk.get("chunk_text")
        )

        sources = [
            {
                "chunk_id": chunk["chunk_id"],
                "lecture_id": chunk["lecture_id"],
                "course_id": chunk["course_id"],
                "chunk_index": chunk["chunk_index"],
                "score": chunk["score"],
            }
            for chunk in sorted_chunks
        ]

        return {           # zz7     هون عم يرع لمرتبين عالاوركستريتر 
            "chunks": sorted_chunks,
            "context_text": context_text,
            "sources": sources,
        }