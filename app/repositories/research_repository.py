from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.research import ResearchHistory
from app.repositories.base_repository import BaseRepository


class ResearchRepository(BaseRepository[ResearchHistory]):
    """Repository for ResearchHistory model operations."""
    
    def __init__(self, db: Session):
        super().__init__(ResearchHistory, db)
    
    def get_user_research_history(self, user_id: int, limit: int = 20) -> List[ResearchHistory]:
        """Get research history for a user."""
        return (
            self.db.query(ResearchHistory)
            .filter(ResearchHistory.user_id == user_id)
            .order_by(ResearchHistory.created_at.desc())
            .limit(limit)
            .all()
        )
    
    def create_research(
        self,
        user_id: int,
        query: str,
        query_type: str,
        summary: Optional[str] = None,
        data_sources: Optional[str] = None,
        confidence_score: Optional[int] = None
    ) -> ResearchHistory:
        """Create a new research record."""
        return self.create(
            user_id=user_id,
            query=query,
            query_type=query_type,
            summary=summary,
            data_sources=data_sources,
            confidence_score=confidence_score
        )
