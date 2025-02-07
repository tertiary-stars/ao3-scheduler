import os
import time
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

def add_chapter(driver, fic_url, chapter_title, chapter_summary, chapter_text,
                chapter_notes_start="", chapter_notes_end="", use_html=False):
    """Adds a new chapter to an existing fic at fic_url."""
    driver.get(fic_url + "/chapters/new")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "chapter_title"))
    )

    # Fill Chapter Title
    driver.find_element(By.ID, "chapter_title").send_keys(chapter_title)

    # Handle Chapter Numbering
    try:
        chapter_pos_field = driver.find_element(By.ID, "chapter_position")
        current_chapter = int(chapter_pos_field.get_attribute("value"))
        try:
            total_chapters_field = driver.find_element(By.ID, "chapter_wip_length")
            total_chapters_field.clear()
            total_chapters_field.send_keys(str(current_chapter + 1))
            print(f"✅ Updated total chapters to {current_chapter + 1}")
        except Exception as e:
            print("⚠️ 'Total chapters' field not found. Skipping chapter total update.")
    except Exception as e:
        print("⚠️ Could not update chapter numbering:", e)

    # Fill Chapter Summary
    driver.find_element(By.ID, "chapter_summary").send_keys(chapter_summary)

    # Handle Chapter Notes (Beginning)
    if chapter_notes_start:
        try:
            front_notes_checkbox = driver.find_element(By.ID, "front-notes-options-show")
            if not front_notes_checkbox.is_selected():
                front_notes_checkbox.click()
            driver.find_element(By.ID, "chapter_notes").send_keys(chapter_notes_start)
            print("✅ Added beginning notes.")
        except Exception as e:
            print("❌ Could not add beginning notes:", e)

    # Handle Chapter Notes (End)
    if chapter_notes_end:
        try:
            end_notes_checkbox = driver.find_element(By.ID, "end-notes-options-show")
            if not end_notes_checkbox.is_selected():
                end_notes_checkbox.click()
            driver.find_element(By.ID, "chapter_endnotes").send_keys(chapter_notes_end)
            print("✅ Added end notes.")
        except Exception as e:
            print("❌ Could not add end notes:", e)

    # Handle Chapter Text Mode Toggle
    try:
        if not use_html:
            rich_text_link = driver.find_element(By.CSS_SELECTOR, "a.rtf-link")
            if "current" not in rich_text_link.get_attribute("class"):
                rich_text_link.click()
                time.sleep(1)
            print("✅ Using Rich Text mode.")
        else:
            html_link = driver.find_element(By.CSS_SELECTOR, "a.html-link")
            if "current" not in html_link.get_attribute("class"):
                html_link.click()
                time.sleep(1)
            print("✅ Using HTML mode.")
    except Exception as e:
        print("⚠️ Mode toggle not found. Defaulting to existing mode.")

    # Fill in Chapter Text using TinyMCE via JavaScript
    try:
        # Wait until the TinyMCE iframe is available and switch into it
        WebDriverWait(driver, 20).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "content_ifr"))
        )
        # Set the content using JavaScript
        driver.execute_script("document.body.innerHTML = arguments[0];", chapter_text)
        print("✅ Filled chapter text using JavaScript.")
        driver.switch_to.default_content()
    except Exception as e:
        print("❌ Could not fill chapter text:", e)

    # Submit the chapter form
    try:
        submit_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='post_without_preview_button']"))
        )
        try:
            submit_button.click()
        except Exception as e:
            # Fallback: JavaScript click
            driver.execute_script("arguments[0].click();", submit_button)
        # Increase wait time for submission confirmation
        WebDriverWait(driver, 40).until(EC.url_contains("/chapters/"))
        print(f"✅ Chapter '{chapter_title}' added successfully!")
    except Exception as e:
        print("❌ Failed to submit chapter:", e)


if __name__ == "__main__":
    driver = webdriver.Chrome()
    login_to_ao3(driver)
    
    # Set fic URL to your work's URL using ID 62825725
    fic_url = "https://archiveofourown.org/works/62825725"
    
    # Prompt for chapter details
    chapter_title = input("Enter chapter title: ")
    chapter_summary = input("Enter chapter summary: ")
    chapter_notes_start = input("Enter beginning notes (leave blank if none): ")
    chapter_notes_end = input("Enter end notes (leave blank if none): ")
    chapter_text = input("Enter chapter content: ")
    mode_choice = input("Enter 'html' to use HTML mode, or leave blank for Rich Text mode: ").strip().lower()
    use_html = True if mode_choice == "html" else False

    add_chapter(
        driver,
        fic_url=fic_url,
        chapter_title=chapter_title,
        chapter_summary=chapter_summary,
        chapter_text=chapter_text,
        chapter_notes_start=chapter_notes_start,
        chapter_notes_end=chapter_notes_end,
        use_html=use_html
    )

    driver.quit()
