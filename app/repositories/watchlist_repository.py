from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.watchlist import CompanyWatchlist
from app.repositories.base_repository import BaseRepository


class WatchlistRepository(BaseRepository[CompanyWatchlist]):
    """Repository for CompanyWatchlist model operations."""
    
    def __init__(self, db: Session):
        super().__init__(CompanyWatchlist, db)
    
    def get_user_watchlist(self, user_id: int) -> List[CompanyWatchlist]:
        """Get all watchlist items for a user."""
        return (
            self.db.query(CompanyWatchlist)
            .filter(
                CompanyWatchlist.user_id == user_id,
                CompanyWatchlist.is_active == True
            )
            .order_by(CompanyWatchlist.created_at.desc())
            .all()
        )
    
    def get_by_symbol(self, user_id: int, symbol: str) -> Optional[CompanyWatchlist]:
        """Get a watchlist item by user and symbol."""
        return (
            self.db.query(CompanyWatchlist)
            .filter(
                CompanyWatchlist.user_id == user_id,
                CompanyWatchlist.symbol == symbol.upper(),
                CompanyWatchlist.is_active == True
            )
            .first()
        )
    
    def add_to_watchlist(
        self, 
        user_id: int, 
        symbol: str, 
        company_name: Optional[str] = None,
        notes: Optional[str] = None
    ) -> CompanyWatchlist:
        """Add a company to watchlist or update if exists."""
        existing = self.get_by_symbol(user_id, symbol)
        if existing:
            return self.update(existing, company_name=company_name, notes=notes)
        return self.create(
            user_id=user_id,
            symbol=symbol.upper(),
            company_name=company_name,
            notes=notes
        )
    
    def remove_from_watchlist(self, user_id: int, symbol: str) -> bool:
        """Remove a company from watchlist (soft delete)."""
        item = self.get_by_symbol(user_id, symbol)
        if item:
            self.update(item, is_active=False)
            return True
        return False
    
    def set_price_alert(
        self,
        user_id: int,
        symbol: str,
        alert_above: Optional[float] = None,
        alert_below: Optional[float] = None
    ) -> Optional[CompanyWatchlist]:
        """Set price alerts for a watchlist item."""
        item = self.get_by_symbol(user_id, symbol)
        if item:
            return self.update(
                item,
                alert_price_above=alert_above,
                alert_price_below=alert_below
            )
        return None
    
    def get_items_with_alerts(self, user_id: int) -> List[CompanyWatchlist]:
        """Get watchlist items that have price alerts set."""
        return (
            self.db.query(CompanyWatchlist)
            .filter(
                CompanyWatchlist.user_id == user_id,
                CompanyWatchlist.is_active == True,
                (CompanyWatchlist.alert_price_above.isnot(None)) |
                (CompanyWatchlist.alert_price_below.isnot(None))
            )
            .all()
        )
    
    def update_watchlist_notes(
        self,
        user_id: int,
        symbol: str,
        notes: str
    ) -> Optional[CompanyWatchlist]:
        """Update notes for a watchlist item."""
        item = self.get_by_symbol(user_id, symbol)
        if item:
            return self.update(item, notes=notes)
        return None
