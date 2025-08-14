import requests
from bs4 import BeautifulSoup
import time
import json
import os

# ========== CONFIG ==========
SEARCH_URL = "https://www.freelancermap.de/projektboerse.html?q=Data+Analyst"
BOT_TOKEN = "8345108637:AAFJHMqhLlbwhim-ePP1JgGtZ0T8cFsmnpw"       # From BotFather
CHAT_ID = "5892654326"           # From @userinfobot
CACHE_FILE = "seen_jobs.json"
CHECK_INTERVAL = 60  # seconds
# ============================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, data=payload)

def load_seen_jobs():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_seen_jobs(jobs):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(jobs, f)

def fetch_jobs():
    response = requests.get(SEARCH_URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    job_cards = soup.select("div.project-box")  # Based on site structure
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
        print("Checking for new jobs...")
        jobs = fetch_jobs()
        new_jobs = [job for job in jobs if job not in seen_jobs]

        for job in new_jobs:
            message = f"🚨 New Data Analyst Job:\n<b>{job['title']}</b>\n{job['link']}"
            send_telegram(message)
            print(f"Sent alert: {job['title']}")

        if new_jobs:
            seen_jobs.extend(new_jobs)
            save_seen_jobs(seen_jobs)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()

