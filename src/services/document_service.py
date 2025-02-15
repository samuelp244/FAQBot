from PyPDF2 import PdfReader
import chromadb
import openai
from typing import List, Dict
from fastapi import UploadFile
import tempfile
import uuid
from src.config import config

class DocumentService:
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

    async def process_document(self, file: UploadFile) -> str:
        """Process uploaded document: convert to text, chunk, embed, and store"""
        document_id = str(uuid.uuid4())
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            try:
                # Extract text from PDF
                reader = PdfReader(temp_file.name)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                
                # Split text into chunks (simple implementation - could be improved)
                chunks = self._split_text(text)
                
                # Generate embeddings and store in ChromaDB
                embeddings = await self._generate_embeddings(chunks)
                
                self.collection.add(
                    documents=chunks,
                    metadatas=[{"document_id": document_id, "filename": file.filename} for _ in chunks],
                    ids=[f"{document_id}_{i}" for i in range(len(chunks))]
                )
                
                return document_id
            finally:
                os.unlink(temp_file.name)

    async def list_documents(self) -> List[Dict]:
        """List all stored documents"""
        # Get unique document IDs from metadata
        results = self.collection.get()
        documents = {}
        
        for metadata in results['metadatas']:
            doc_id = metadata['document_id']
            if doc_id not in documents:
                documents[doc_id] = {
                    'document_id': doc_id,
                    'filename': metadata['filename']
                }
        
        return list(documents.values())

    async def delete_document(self, document_id: str):
        """Delete a document and its chunks from the database"""
        # Get all chunk IDs for the document
        results = self.collection.get(
            where={"document_id": document_id}
        )
        
        if not results['ids']:
            raise ValueError(f"Document {document_id} not found")
        
        # Delete all chunks
        self.collection.delete(
            where={"document_id": document_id}
        )

    def _split_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks of approximately equal size"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_size += len(word) + 1  # +1 for space
            if current_size > chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_size = len(word)
            else:
                current_chunk.append(word)
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks

    async def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks using OpenAI"""
        embeddings = []
        for text in texts:
            response = await self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            embeddings.append(response.data[0].embedding)
        return embeddings
