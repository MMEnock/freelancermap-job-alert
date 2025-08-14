import requests
from bs4 import BeautifulSoup
import time
import json
import os

# ========== CONFIG ==========
SEARCH_URL = "https://www.freelancermap.de/projektboerse.html?q=Data+Analyst"
BOT_TOKEN = os.getenv("BOT_TOKEN")   # Railway environment variable
CHAT_ID = os.getenv("CHAT_ID")       # Railway environment variable
CACHE_FILE = "seen_jobs.json"
CHECK_INTERVAL = 60  # seconds
# ============================

def send_telegram(message):
    """Send a message via Telegram bot."""
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Missing BOT_TOKEN or CHAT_ID in environment variables.")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"❌ Telegram send error: {e}")

def load_seen_jobs():
    """Load already seen jobs from file."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_seen_jobs(jobs):
    """Save seen jobs to file."""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(jobs, f)

def fetch_jobs():
    """Scrape jobs from Freelancermap search results."""
    try:
        response = requests.get(SEARCH_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Error fetching jobs: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    job_cards = soup.select("div.project-box")  # May need adjustment if site changes
    jobs = []

    for card in job_cards:
        title_tag = card.select_one("h2 a")
        if title_tag:
            title = title_tag.text.strip()
            link = "https://www.freelancermap.de" + title_tag["href"]
            jobs.append({"title": title, "link": link})

    return jobs

def main():
    seen_jobs = load_seen_jobs()

    while True:
        print("🔍 Checking for new jobs...")
        jobs = fetch_jobs()
        new_jobs = [job for job in jobs if job not in seen_jobs]

        for job in new_jobs:
            message = f"🚨 New Data Analyst Job:\n<b>{job['title']}</b>\n{job['link']}"
            send_telegram(message)
            print(f"✅ Alert sent: {job['title']}")

        if new_jobs:
            seen_jobs.extend(new_jobs)
            save_seen_jobs(seen_jobs)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
