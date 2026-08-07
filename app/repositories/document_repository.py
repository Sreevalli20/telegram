from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.document import Document
from app.repositories.base_repository import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """Repository for Document model operations."""
    
    def __init__(self, db: Session):
        super().__init__(Document, db)
    
    def get_user_documents(self, user_id: int, limit: int = 20) -> List[Document]:
        """Get documents for a user."""
        return (
            self.db.query(Document)
            .filter(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .limit(limit)
            .all()
        )
    
    def get_by_file_id(self, file_id: int) -> Optional[Document]:
        """Get document by Telegram file ID."""
        return self.db.query(Document).filter(Document.file_id == file_id).first()
    
    def create_document(
        self,
        user_id: int,
        file_type: str,
        file_id: Optional[int] = None,
        file_name: Optional[str] = None,
        file_path: Optional[str] = None,
        file_size: Optional[int] = None,
        conversation_id: Optional[int] = None
    ) -> Document:
        """Create a new document record."""
        return self.create(
            user_id=user_id,
            file_type=file_type,
            file_id=file_id,
            file_name=file_name,
            file_path=file_path,
            file_size=file_size,
            conversation_id=conversation_id,
            processing_status="pending"
        )
    
    def update_processing_status(
        self,
        document: Document,
        status: str,
        extracted_text: Optional[str] = None,
        analysis_summary: Optional[str] = None
    ) -> Document:
        """Update document processing status."""
        return self.update(
            document,
            processing_status=status,
            extracted_text=extracted_text,
            analysis_summary=analysis_summary
        )
