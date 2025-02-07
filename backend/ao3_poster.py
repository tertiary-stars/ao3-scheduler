import os
import time
import sqlite3
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# Load environment variables
load_dotenv()
AO3_USERNAME = os.getenv("AO3_USERNAME")
AO3_PASSWORD = os.getenv("AO3_PASSWORD")
DATABASE_PATH = "backend/ao3_scheduler.db"  # Update as needed

def get_next_scheduled_fic():
    """Fetch the next pending scheduled fic from the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, fandoms, rating, warnings, category, language, summary, content, tags, relationships, characters, author_notes, end_notes, is_complete FROM scheduled_fics WHERE status = 'pending' ORDER BY scheduled_time ASC LIMIT 1"
    )
    fic = cursor.fetchone()
    conn.close()
    if fic:
        return {
            "id": fic[0],
            "title": fic[1],
            "fandoms": fic[2],
            "rating": fic[3],
            "warnings": fic[4],
            "category": fic[5],
            "language": fic[6],
            "summary": fic[7],
            "content": fic[8],
            "tags": fic[9],
            "relationships": fic[10],
            "characters": fic[11],
            "author_notes": fic[12],
            "end_notes": fic[13],
            "is_complete": fic[14],
        }
    return None

def mark_fic_as_posted(fic_id):
    """Update the database to mark the fic as posted."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE scheduled_fics SET status = 'posted' WHERE id = ?", (fic_id,))
    conn.commit()
    conn.close()
    print(f"✅ Fic ID {fic_id} marked as posted!")

def login_to_ao3(driver):
    """Logs into AO3 using the login popup and redirects to 'My Works' page."""
    driver.get("https://archiveofourown.org/")
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Log In"))
    ).click()
    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.NAME, "user[login]"))
    ).send_keys(AO3_USERNAME)
    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.NAME, "user[password]"))
    ).send_keys(AO3_PASSWORD)
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
    ).click()
    WebDriverWait(driver, 20).until_not(
        EC.presence_of_element_located((By.LINK_TEXT, "Log In"))
    )
    print("✅ Login successful!")
    # Redirect to "My Works" page
    driver.get(f"https://archiveofourown.org/users/{AO3_USERNAME}/works")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "work"))
    )
    print("📂 Redirected to 'My Works' page.")

def post_fic_on_ao3():
    """Fetches the next scheduled fic and posts it on AO3 as a new work."""
    fic = get_next_scheduled_fic()
    if not fic:
        print("📭 No fics to post at this time.")
        return

    print(f"📢 Posting fic: {fic['title']}")

    driver = webdriver.Chrome()
    login_to_ao3(driver)

    # Navigate to "Post New Work" page
    driver.get("https://archiveofourown.org/works/new")
    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.ID, "work_title"))
    )

    # Fill in the New Work form:
    # Title
    driver.find_element(By.ID, "work_title").send_keys(fic["title"])

    # Fandom (autocomplete)
    try:
        fandom_field = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "work_fandom_autocomplete"))
        )
        fandom_field.click()
        time.sleep(1)
        fandom_field.send_keys(fic["fandoms"])
        time.sleep(2)
        fandom_field.send_keys(Keys.DOWN)
        time.sleep(1)
        fandom_field.send_keys(Keys.RETURN)
        print(f"✅ Fandom '{fic['fandoms']}' selected successfully!")
    except Exception as e:
        print("❌ Could not enter fandom:", e)

    # Dropdown selections for Rating, Warnings, Category, Language
    dropdowns = {
        "Rating": ("work_rating", fic["rating"]),
        "Warnings": ("work_warnings", fic["warnings"]),
        "Category": ("work_category", fic["category"]),
        "Language": ("work_language_id", fic["language"]),
    }
    for label, (dropdown_id, value) in dropdowns.items():
        try:
            dropdown_element = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, dropdown_id))
            )
            select = Select(dropdown_element)
            select.select_by_visible_text(value)
            print(f"✅ Selected {label}: {value}")
        except Exception as e:
            print(f"❌ Could not select {label}: {e}")

    # Fill in Summary
    try:
        summary_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "work_summary"))
        )
        summary_field.send_keys(fic["summary"])
        print("✅ Filled summary.")
    except Exception as e:
        print("❌ Could not fill summary:", e)

    # Fill in Content (Fic Text)
    try:
        # Assume the content is edited using TinyMCE;
        # switch to its iframe (we assume the editor iframe id is "content_ifr")
        WebDriverWait(driver, 20).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "content_ifr"))
        )
        driver.execute_script("document.body.innerHTML = arguments[0];", fic["content"])
        print("✅ Filled content using JavaScript in TinyMCE.")
        driver.switch_to.default_content()
    except Exception as e:
        print("❌ Could not fill content:", e)

    # Optionally, fill in additional fields if they exist:
    # Tags, Relationships, Characters, Author Notes, End Notes
    # (Implement similar to above if needed)

    # Submit the New Work form
    try:
        submit_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
        )
        submit_button.click()
        WebDriverWait(driver, 40).until(EC.url_contains("/works/"))
        print("✅ Fic posted successfully!")
        mark_fic_as_posted(fic["id"])
    except Exception as e:
        print("❌ Failed to submit fic:", e)

    driver.quit()


if __name__ == "__main__":
    post_fic_on_ao3()
