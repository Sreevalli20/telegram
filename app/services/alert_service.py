"""Alert service for managing price and news alerts."""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.repositories.watchlist_repository import WatchlistRepository
from app.repositories.notification_repository import NotificationRepository
from app.finance import MarketDataService, NewsService
from datetime import datetime, timedelta


class AlertService:
    """Service for managing intelligent alerts."""
    
    def __init__(self, db: Session):
        self.db = db
        self.watchlist_repo = WatchlistRepository(db)
        self.notification_repo = NotificationRepository(db)
        self.market_data = MarketDataService()
        self.news_service = NewsService()
    
    async def check_price_alerts(self, user_id: int) -> List[Dict[str, Any]]:
        """Check and trigger price alerts for a user."""
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
            alert_threshold = None
            
            if item.alert_price_above and current_price >= item.alert_price_above:
                triggered = True
                alert_type = "above"
                alert_threshold = item.alert_price_above
            elif item.alert_price_below and current_price <= item.alert_price_below:
                triggered = True
                alert_type = "below"
                alert_threshold = item.alert_price_below
            
            if triggered:
                alert_message = f"🚨 Price Alert: {item.symbol} is now trading at {current_price}, which is {alert_type} your alert of {alert_threshold}"
                
                # Create notification
                self.notification_repo.create(
                    user_id=user_id,
                    notification_type="price_alert",
                    title=f"Price Alert: {item.symbol}",
                    message=alert_message,
                    data={
                        "symbol": item.symbol,
                        "current_price": current_price,
                        "alert_type": alert_type,
                        "alert_threshold": alert_threshold
                    }
                )
                
                triggered_alerts.append({
                    "symbol": item.symbol,
                    "current_price": current_price,
                    "alert_type": alert_type,
                    "alert_threshold": alert_threshold,
                    "message": alert_message
                })
        
        return triggered_alerts
    
    async def check_price_movement_alerts(self, user_id: int, threshold_percent: float = 5.0) -> List[Dict[str, Any]]:
        """Check for significant price movements in watchlist."""
        watchlist_items = self.watchlist_repo.get_user_watchlist(user_id)
        
        significant_movements = []
        for item in watchlist_items:
            price_data = await self.market_data.get_stock_price(item.symbol)
            
            if not price_data.get("available"):
                continue
            
            change_percent = price_data.get("change_percent", 0)
            
            if abs(change_percent) >= threshold_percent:
                direction = "up" if change_percent > 0 else "down"
                movement_message = f"📊 {item.symbol} moved {direction} by {abs(change_percent):.2f}% today"
                
                # Create notification
                self.notification_repo.create(
                    user_id=user_id,
                    notification_type="price_movement",
                    title=f"Price Movement: {item.symbol}",
                    message=movement_message,
                    data={
                        "symbol": item.symbol,
                        "change_percent": change_percent,
                        "current_price": price_data.get("current_price")
                    }
                )
                
                significant_movements.append({
                    "symbol": item.symbol,
                    "change_percent": change_percent,
                    "direction": direction,
                    "message": movement_message
                })
        
        return significant_movements
    
    async def check_news_alerts(self, user_id: int) -> List[Dict[str, Any]]:
        """Check for important news about watchlist items."""
        watchlist_items = self.watchlist_repo.get_user_watchlist(user_id)
        
        important_news = []
        for item in watchlist_items:
            # Get recent news for the company
            company_news = await self.news_service.get_company_news(item.symbol, limit=5)
            
            # Check for news in the last 24 hours
            recent_news = []
            now = datetime.now()
            for news_item in company_news:
                published = news_item.get("published")
                if published:
                    published_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
                    if now - published_date <= timedelta(hours=24):
                        recent_news.append(news_item)
            
            if recent_news:
                for news_item in recent_news[:2]:  # Top 2 recent news items
                    news_message = f"📰 News: {news_item.get('title')}"
                    
                    # Create notification
                    self.notification_repo.create(
                        user_id=user_id,
                        notification_type="news_alert",
                        title=f"News: {item.symbol}",
                        message=news_message,
                        data={
                            "symbol": item.symbol,
                            "news_title": news_item.get("title"),
                            "news_link": news_item.get("link"),
                            "source": news_item.get("source")
                        }
                    )
                    
                    important_news.append({
                        "symbol": item.symbol,
                        "news_title": news_item.get("title"),
                        "source": news_item.get("source"),
                        "message": news_message
                    })
        
        return important_news
    
    async def check_earnings_alerts(self, user_id: int) -> List[Dict[str, Any]]:
        """Check for upcoming earnings announcements."""
        watchlist_items = self.watchlist_repo.get_user_watchlist(user_id)
        
        upcoming_earnings = []
        earnings_calendar = await self.news_service.get_earnings_calendar(days=7)
        
        for item in watchlist_items:
            for earnings in earnings_calendar:
                if earnings["symbol"].upper() == item.symbol.upper():
                    earnings_message = f"📅 Earnings: {item.symbol} reporting on {earnings['date']}"
                    
                    # Create notification
                    self.notification_repo.create(
                        user_id=user_id,
                        notification_type="earnings_alert",
                        title=f"Upcoming Earnings: {item.symbol}",
                        message=earnings_message,
                        data={
                            "symbol": item.symbol,
                            "earnings_date": earnings["date"],
                            "estimated_eps": earnings.get("estimated_eps"),
                            "previous_eps": earnings.get("previous_eps")
                        }
                    )
                    
                    upcoming_earnings.append({
                        "symbol": item.symbol,
                        "earnings_date": earnings["date"],
                        "estimated_eps": earnings.get("estimated_eps"),
                        "message": earnings_message
                    })
        
        return upcoming_earnings
    
    async def check_all_alerts(self, user_id: int) -> Dict[str, Any]:
        """Check all types of alerts for a user."""
        price_alerts = await self.check_price_alerts(user_id)
        movement_alerts = await self.check_price_movement_alerts(user_id, threshold_percent=5.0)
        news_alerts = await self.check_news_alerts(user_id)
        earnings_alerts = await self.check_earnings_alerts(user_id)
        
        return {
            "price_alerts": price_alerts,
            "movement_alerts": movement_alerts,
            "news_alerts": news_alerts,
            "earnings_alerts": earnings_alerts,
            "total_alerts": len(price_alerts) + len(movement_alerts) + len(news_alerts) + len(earnings_alerts)
        }
    
    def get_user_notifications(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent notifications for a user."""
        notifications = self.notification_repo.get_user_notifications(user_id, limit=limit)
        
        return [
            {
                "id": notif.id,
                "type": notif.notification_type,
                "title": notif.title,
                "message": notif.message,
                "data": notif.data,
                "is_read": notif.is_read,
                "created_at": notif.created_at.isoformat() if notif.created_at else None
            }
            for notif in notifications
        ]
    
    def mark_notification_read(self, user_id: int, notification_id: int) -> bool:
        """Mark a notification as read."""
        notification = self.notification_repo.get_by_id(notification_id)
        if notification and notification.user_id == user_id:
            self.notification_repo.update(notification, is_read=True)
            return True
        return False
    
    def mark_all_notifications_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user."""
        notifications = self.notification_repo.get_user_notifications(user_id, limit=100)
        count = 0
        for notif in notifications:
            if not notif.is_read:
                self.notification_repo.update(notif, is_read=True)
                count += 1
        return count
