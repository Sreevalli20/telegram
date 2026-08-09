"""Watchlist service for managing user watchlists and alerts."""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.repositories.watchlist_repository import WatchlistRepository
from app.finance import MarketDataService, CompanyDataService


class WatchlistService:
    """Service for managing stock watchlists and alerts."""
    
    def __init__(self, db: Session):
        self.db = db
        self.watchlist_repo = WatchlistRepository(db)
        self.market_data = MarketDataService()
        self.company_data = CompanyDataService()
    
    async def add_to_watchlist(
        self,
        user_id: int,
        symbol: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a company to the user's watchlist."""
        symbol = symbol.upper()
        
        # Get company name if available
        company_overview = await self.company_data.get_company_overview(symbol)
        company_name = company_overview.get("company_name") if company_overview.get("available") else None
        
        # Add to watchlist
        watchlist_item = self.watchlist_repo.add_to_watchlist(
            user_id=user_id,
            symbol=symbol,
            company_name=company_name,
            notes=notes
        )
        
        return {
            "success": True,
            "symbol": symbol,
            "company_name": company_name,
            "added": True,
            "message": f"Added {symbol} to your watchlist"
        }
    
    def remove_from_watchlist(self, user_id: int, symbol: str) -> Dict[str, Any]:
        """Remove a company from the user's watchlist."""
        symbol = symbol.upper()
        removed = self.watchlist_repo.remove_from_watchlist(user_id, symbol)
        
        return {
            "success": removed,
            "symbol": symbol,
            "removed": removed,
            "message": f"Removed {symbol} from your watchlist" if removed else f"{symbol} not found in watchlist"
        }
    
    def get_watchlist(self, user_id: int) -> List[Dict[str, Any]]:
        """Get the user's watchlist."""
        watchlist_items = self.watchlist_repo.get_user_watchlist(user_id)
        
        return [
            {
                "id": item.id,
                "symbol": item.symbol,
                "company_name": item.company_name,
                "notes": item.notes,
                "alert_above": item.alert_price_above,
                "alert_below": item.alert_price_below,
                "added_date": item.created_at.isoformat() if item.created_at else None
            }
            for item in watchlist_items
        ]
    
    async def get_watchlist_with prices(self, user_id: int) -> Dict[str, Any]:
        """Get watchlist with current prices."""
        watchlist_items = self.watchlist_repo.get_user_watchlist(user_id)
        
        watchlist_with_prices = []
        for item in watchlist_items:
            price_data = await self.market_data.get_stock_price(item.symbol)
            
            watchlist_with_prices.append({
                "id": item.id,
                "symbol": item.symbol,
                "company_name": item.company_name,
                "current_price": price_data.get("current_price"),
                "change": price_data.get("change"),
                "change_percent": price_data.get("change_percent"),
                "notes": item.notes,
                "alert_above": item.alert_price_above,
                "alert_below": item.alert_price_below,
                "added_date": item.created_at.isoformat() if item.created_at else None
            })
        
        return {
            "watchlist": watchlist_with_prices,
            "count": len(watchlist_with_prices)
        }
    
    def set_price_alert(
        self,
        user_id: int,
        symbol: str,
        alert_above: Optional[float] = None,
        alert_below: Optional[float] = None
    ) -> Dict[str, Any]:
        """Set price alerts for a watchlist item."""
        symbol = symbol.upper()
        
        # First ensure the item is in watchlist
        existing = self.watchlist_repo.get_by_symbol(user_id, symbol)
        if not existing:
            # Add to watchlist first
            self.watchlist_repo.add_to_watchlist(user_id, symbol)
        
        # Set alerts
        updated = self.watchlist_repo.set_price_alert(
            user_id=user_id,
            symbol=symbol,
            alert_above=alert_above,
            alert_below=alert_below
        )
        
        return {
            "success": updated is not None,
            "symbol": symbol,
            "alert_above": alert_above,
            "alert_below": alert_below,
            "message": f"Price alerts set for {symbol}"
        }
    
    def update_notes(
        self,
        user_id: int,
        symbol: str,
        notes: str
    ) -> Dict[str, Any]:
        """Update notes for a watchlist item."""
        symbol = symbol.upper()
        updated = self.watchlist_repo.update_watchlist_notes(user_id, symbol, notes)
        
        return {
            "success": updated is not None,
            "symbol": symbol,
            "notes": notes,
            "message": f"Notes updated for {symbol}"
        }
    
    async def check_alerts(self, user_id: int) -> List[Dict[str, Any]]:
        """Check if any watchlist items have triggered their price alerts."""
        items_with_alerts = self.watchlist_repo.get_items_with_alerts(user_id)
        
        triggered_alerts = []
        for item in items_with_alerts:
            price_data = await self.market_data.get_stock_price(item.symbol)
            
            if not price_data.get("available"):
                continue
            
            current_price = price_data.get("current_price")
            
            # Check if alert is triggered
            triggered = False
            alert_type = None
            
            if item.alert_price_above and current_price >= item.alert_price_above:
                triggered = True
                alert_type = "above"
            elif item.alert_price_below and current_price <= item.alert_price_below:
                triggered = True
                alert_type = "below"
            
            if triggered:
                triggered_alerts.append({
                    "symbol": item.symbol,
                    "company_name": item.company_name,
                    "current_price": current_price,
                    "alert_price": item.alert_price_above if alert_type == "above" else item.alert_price_below,
                    "alert_type": alert_type,
                    "message": f"{item.symbol} is now trading at {current_price}, which is {alert_type} your alert of {item.alert_price_above if alert_type == 'above' else item.alert_price_below}"
                })
        
        return triggered_alerts
    
    async def get_watchlist_summary(self, user_id: int) -> Dict[str, Any]:
        """Get a summary of the user's watchlist performance."""
        watchlist_with_prices = await self.get_watchlist_with_prices(user_id)
        
        if not watchlist_with_prices["watchlist"]:
            return {
                "count": 0,
                "summary": "Your watchlist is empty"
            }
        
        # Calculate summary statistics
        total_items = len(watchlist_with_prices["watchlist"])
        items_with_prices = [item for item in watchlist_with_prices["watchlist"] if item.get("current_price")]
        
        if not items_with_prices:
            return {
                "count": total_items,
                "summary": f"You have {total_items} items in your watchlist. Price data not available."
            }
        
        gainers = [item for item in items_with_prices if item.get("change_percent", 0) > 0]
        losers = [item for item in items_with_prices if item.get("change_percent", 0) < 0]
        
        best_performer = max(items_with_prices, key=lambda x: x.get("change_percent", 0)) if items_with_prices else None
        worst_performer = min(items_with_prices, key=lambda x: x.get("change_percent", 0)) if items_with_prices else None
        
        summary = f"""📊 Watchlist Summary ({total_items} items):

📈 Gainers: {len(gainers)}
📉 Losers: {len(losers)}

Best: {best_performer['symbol']} ({best_performer.get('change_percent', 0):.2f}%) if best_performer else 'N/A'
Worst: {worst_performer['symbol']} ({worst_performer.get('change_percent', 0):.2f}%) if worst_performer else 'N/A'
"""
        
        return {
            "count": total_items,
            "gainers": len(gainers),
            "losers": len(losers),
            "best_performer": best_performer,
            "worst_performer": worst_performer,
            "summary": summary,
            "items": watchlist_with_prices["watchlist"]
        }
