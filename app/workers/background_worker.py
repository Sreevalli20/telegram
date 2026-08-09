"""Background worker service for scheduled tasks using APScheduler."""
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import asyncio
from loguru import logger


class BackgroundWorker:
    """Background worker for scheduled financial tasks."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    def start(self):
        """Start the background scheduler."""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("Background worker started")
    
    def shutdown(self):
        """Shutdown the background scheduler."""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Background worker shutdown")
    
    def add_job(
        self,
        func,
        trigger_type: str = "interval",
        trigger_args: Optional[dict] = None,
        job_id: Optional[str] = None,
        replace_existing: bool = True
    ):
        """Add a job to the scheduler."""
        if trigger_args is None:
            trigger_args = {}
        
        if trigger_type == "interval":
            trigger = IntervalTrigger(**trigger_args)
        elif trigger_type == "cron":
            trigger = CronTrigger(**trigger_args)
        else:
            raise ValueError(f"Unknown trigger type: {trigger_type}")
        
        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            replace_existing=replace_existing
        )
        logger.info(f"Job added: {job_id or 'unnamed'} with trigger {trigger_type}")
    
    def remove_job(self, job_id: str):
        """Remove a job from the scheduler."""
        self.scheduler.remove_job(job_id)
        logger.info(f"Job removed: {job_id}")
    
    def get_jobs(self):
        """Get all scheduled jobs."""
        return self.scheduler.get_jobs()
    
    async def run_alert_check_job(self, alert_service, user_id: int):
        """Job to check and trigger alerts for a user."""
        try:
            logger.info(f"Running alert check for user {user_id}")
            alerts = await alert_service.check_all_alerts(user_id)
            
            if alerts["total_alerts"] > 0:
                logger.info(f"Found {alerts['total_alerts']} alerts for user {user_id}")
                # Here you would send notifications via Telegram
                # This would be handled by the notification service
        except Exception as e:
            logger.error(f"Error in alert check job: {e}")
    
    async def run_daily_briefing_job(self, daily_intelligence_service, user_id: int, briefing_type: str = "morning"):
        """Job to generate and send daily briefings."""
        try:
            logger.info(f"Running {briefing_type} briefing for user {user_id}")
            
            if briefing_type == "morning":
                briefing = await daily_intelligence_service.generate_morning_brief(user_id)
            else:
                briefing = await daily_intelligence_service.generate_evening_summary(user_id)
            
            logger.info(f"Generated {briefing_type} briefing for user {user_id}")
            # Here you would send the briefing via Telegram
        except Exception as e:
            logger.error(f"Error in daily briefing job: {e}")
    
    async def run_watchlist_summary_job(self, watchlist_service, user_id: int):
        """Job to generate watchlist summary."""
        try:
            logger.info(f"Running watchlist summary for user {user_id}")
            summary = await watchlist_service.get_watchlist_summary(user_id)
            logger.info(f"Generated watchlist summary for user {user_id}")
            # Here you would send the summary via Telegram
        except Exception as e:
            logger.error(f"Error in watchlist summary job: {e}")
    
    def schedule_alert_checks(self, alert_service, user_id: int, interval_minutes: int = 15):
        """Schedule periodic alert checks for a user."""
        job_id = f"alert_check_{user_id}"
        self.add_job(
            func=lambda: asyncio.create_task(self.run_alert_check_job(alert_service, user_id)),
            trigger_type="interval",
            trigger_args={"minutes": interval_minutes},
            job_id=job_id
        )
    
    def schedule_daily_briefings(
        self,
        daily_intelligence_service,
        user_id: int,
        morning_time: str = "08:00",
        evening_time: str = "18:00"
    ):
        """Schedule daily morning and evening briefings."""
        # Morning briefing
        morning_hour, morning_minute = map(int, morning_time.split(":"))
        self.add_job(
            func=lambda: asyncio.create_task(
                self.run_daily_briefing_job(daily_intelligence_service, user_id, "morning")
            ),
            trigger_type="cron",
            trigger_args={"hour": morning_hour, "minute": morning_minute},
            job_id=f"morning_briefing_{user_id}"
        )
        
        # Evening briefing
        evening_hour, evening_minute = map(int, evening_time.split(":"))
        self.add_job(
            func=lambda: asyncio.create_task(
                self.run_daily_briefing_job(daily_intelligence_service, user_id, "evening")
            ),
            trigger_type="cron",
            trigger_args={"hour": evening_hour, "minute": evening_minute},
            job_id=f"evening_briefing_{user_id}"
        )
    
    def schedule_watchlist_summary(self, watchlist_service, user_id: int, interval_hours: int = 4):
        """Schedule periodic watchlist summaries."""
        job_id = f"watchlist_summary_{user_id}"
        self.add_job(
            func=lambda: asyncio.create_task(self.run_watchlist_summary_job(watchlist_service, user_id)),
            trigger_type="interval",
            trigger_args={"hours": interval_hours},
            job_id=job_id
        )
    
    def schedule_earnings_check(self, alert_service, user_id: int, interval_hours: int = 6):
        """Schedule periodic earnings calendar checks."""
        job_id = f"earnings_check_{user_id}"
        
        async def earnings_check():
            try:
                logger.info(f"Running earnings check for user {user_id}")
                earnings = await alert_service.check_earnings_alerts(user_id)
                logger.info(f"Found {len(earnings)} upcoming earnings for user {user_id}")
            except Exception as e:
                logger.error(f"Error in earnings check job: {e}")
        
        self.add_job(
            func=lambda: asyncio.create_task(earnings_check()),
            trigger_type="interval",
            trigger_args={"hours": interval_hours},
            job_id=job_id
        )
    
    def unschedule_user_jobs(self, user_id: int):
        """Unschedule all jobs for a specific user."""
        job_ids = [job.id for job in self.get_jobs() if str(user_id) in job.id]
        for job_id in job_ids:
            self.remove_job(job_id)
        logger.info(f"Unscheduled {len(job_ids)} jobs for user {user_id}")
