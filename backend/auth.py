import os
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get session file path from .env
SESSION_FILE = os.getenv("SESSION_FILE", "backend/ao3_session.json")

def save_session(cookies):
    """Save session cookies to a file."""
    with open(SESSION_FILE, "w") as session_file:
        json.dump(cookies, session_file)

def load_session():
    """Load session cookies if available."""
    if os.path.exists(SESSION_FILE):
        if os.path.getsize(SESSION_FILE) > 0:  # Check if file is not empty
            with open(SESSION_FILE, "r") as session_file:
                try:
                    cookies = json.load(session_file)
                    return requests.utils.cookiejar_from_dict(cookies)
                except json.JSONDecodeError:
                    print("⚠️ Warning: Session file is corrupted. Resetting session.")
                    os.remove(SESSION_FILE)
    return None

def check_session_valid(session):
    """Check if an existing session is still valid by visiting a known page."""
    test_url = "https://archiveofourown.org/"
    response = session.get(test_url)
    return "Log In" not in response.text  # If "Log In" is not found, the session is valid

def ao3_login(username: str = None, password: str = None):
    """Log in to AO3, using a stored session if available."""
    session = requests.Session()

    # Try to load an existing session
    existing_cookies = load_session()
    if existing_cookies:
        session.cookies.update(existing_cookies)
        if check_session_valid(session):
            return {"status": "success", "message": "Using saved session!"}

    # Use environment variables if no credentials are provided
    if username is None:
        username = os.getenv("AO3_USERNAME")
    if password is None:
        password = os.getenv("AO3_PASSWORD")

    if not username or not password:
        return {"status": "error", "message": "AO3 credentials missing!"}

    # If no valid session, proceed with login
    login_url = "https://archiveofourown.org/users/login"
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.text, "html.parser")

    csrf_token = soup.find("input", {"name": "authenticity_token"})
    if not csrf_token:
        return {"status": "error", "message": "CSRF token not found!"}

    payload = {
        "user[login]": username,
        "user[password]": password,
        "authenticity_token": csrf_token["value"],
        "commit": "Log in"
    }

    response = session.post(login_url, data=payload)

    if "Successfully logged in" in response.text or f"Hi, {username}" in response.text:
        save_session(session.cookies.get_dict())
        return {"status": "success", "message": "Login successful!"}

    elif "user_session" in session.cookies.get_dict():
        save_session(session.cookies.get_dict())
        return {"status": "success", "message": "Login successful (via session cookie)!"}

    else:
        return {"status": "error", "message": "Login failed!"}
    
def ao3_logout():
    """Clears the saved AO3 session."""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)  # Delete the session file
        return {"status": "success", "message": "Logged out successfully!"}
    return {"status": "error", "message": "No active session found."}

