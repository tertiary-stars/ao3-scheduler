from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from database import SessionLocal, ScheduledFic
from datetime import datetime
import pytz

scheduler = BackgroundScheduler()
scheduler_started = False  # Prevent multiple starts

def post_fic(fic):
    """Simulate fic posting to AO3 (replace with automation later)."""
    print(f"📢 Posting fic: {fic.title}")
    # TODO: Add AO3 web automation here (using Selenium/Playwright)

def check_and_post_fics():
    """Check database for fics that need to be posted and post them."""
    db: Session = SessionLocal()
    now_utc = datetime.utcnow().replace(tzinfo=pytz.UTC)
    
    print(f"🔍 Checking for scheduled fics at {now_utc}")  # Debug log

    pending_fics = db.query(ScheduledFic).filter(
        ScheduledFic.scheduled_time <= now_utc,
        ScheduledFic.status == "pending"
    ).all()

    if not pending_fics:
        print("📭 No fics to post right now.")  # Debug log

    for fic in pending_fics:
        print(f"📢 Posting fic: {fic.title}")
        # TODO: Replace with AO3 automation
        fic.status = "posted"
        db.commit()
        print(f"✅ Fic '{fic.title}' marked as posted!")

    db.close()

def start_scheduler():
    """Starts the cron job to check for scheduled fics every 5 minutes."""
    global scheduler_started
    if not scheduler_started:
        scheduler.add_job(check_and_post_fics, "interval", minutes=5)
        scheduler.start()
        scheduler_started = True  # Mark scheduler as started
        print("⏳ Fic scheduler is running every 5 minutes...")
