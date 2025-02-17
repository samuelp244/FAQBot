import chromadb
import openai
from typing import List
from src.config import config

class QueryService:
    def __init__(self):
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="db")
        self.collection = self.chroma_client.get_or_create_collection("documents")
        
        # Initialize OpenAI client
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in your .env file.")
        self.openai_client = openai.OpenAI(
            api_key=config.OPENAI_API_KEY
        )

    async def generate_answer(self, question: str) -> str:
        """Generate an answer using RAG with ChromaDB and OpenAI"""
        # Generate embedding for the question
        question_embedding = self._generate_embedding(question)
        
        # Query ChromaDB for relevant chunks
        results = self.collection.query(
            query_embeddings=[question_embedding],
            n_results=3  # Get top 3 most relevant chunks
        )
        
        if not results['documents']:
            return "I couldn't find any relevant information to answer your question."
        
        # Combine relevant chunks into context
        context = "\n\n".join(results['documents'][0])
        
        # Generate answer using OpenAI
        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Answer the question based on the provided context. If you cannot find the answer in the context, say so."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
            ]
        )
        
        return response.choices[0].message.content

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text using OpenAI"""
        response = self.openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
