from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from src.services.document_service import DocumentService

router = APIRouter(tags=["documents"])
document_service = DocumentService()

@router.post("/upload-docs/")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        result = await document_service.process_document(file)
        return {"message": "Document processed successfully", "document_id": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list-docs/")
async def list_documents():
    """List all stored documents"""
    try:
        documents = await document_service.list_documents()
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-doc/{document_id}")
async def delete_document(document_id: str):
    """Delete a document by ID"""
    try:
        await document_service.delete_document(document_id)
        return {"message": f"Document {document_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
