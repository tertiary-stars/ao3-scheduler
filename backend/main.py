from fastapi import FastAPI, Form, Depends
from auth import ao3_login, ao3_logout
from dotenv import load_dotenv
import requests
import uvicorn

from sqlalchemy.orm import Session
from database import SessionLocal, ScheduledFic
from datetime import datetime
import pytz

load_dotenv()  # Load environment variables

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/logout")
def logout():
    """Endpoint to clear the AO3 session."""
    result = ao3_logout()
    return result

@app.post("/login")
def login(username: str = Form(None), password: str = Form(None)):
    """Login with optional credentials (fallback to .env)."""
    result = ao3_login(username, password)
    return result

@app.get("/session-status")
def check_session():
    """Endpoint to check if a valid session exists."""
    from auth import load_session, check_session_valid
    session = requests.Session()
    existing_cookies = load_session()
    
    if existing_cookies:
        session.cookies.update(existing_cookies)
        if check_session_valid(session):
            return {"status": "success", "message": "Session is valid!"}
    
    return {"status": "error", "message": "No valid session found."}

@app.post("/schedule-fic")
def schedule_fic(
    title: str = Form(...),
    fandoms: str = Form(...),  # Comma-separated
    rating: str = Form(...),
    warnings: str = Form(...),
    category: str = Form(...),
    language: str = Form(...),
    summary: str = Form(...),
    content: str = Form(...),
    tags: str = Form(None),  # Optional
    relationships: str = Form(None),  # Optional
    characters: str = Form(None),  # Optional
    author_notes: str = Form(None),  # Optional
    end_notes: str = Form(None),  # Optional
    is_complete: bool = Form(False),
    scheduled_time: str = Form(...),  # Format: "YYYY-MM-DD HH:MM"
    db: Session = Depends(get_db)
):
    """Schedule a fic to be posted at a future date with all AO3 required fields."""
    try:
        # Convert string to datetime (assuming UTC)
        scheduled_dt = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M").replace(tzinfo=pytz.UTC)

        new_fic = ScheduledFic(
            title=title, fandoms=fandoms, rating=rating, warnings=warnings,
            category=category, language=language, summary=summary,
            content=content, tags=tags, relationships=relationships,
            characters=characters, author_notes=author_notes, end_notes=end_notes,
            is_complete=is_complete, scheduled_time=scheduled_dt
        )
        db.add(new_fic)
        db.commit()
        return {"status": "success", "message": "Fic scheduled successfully!"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
