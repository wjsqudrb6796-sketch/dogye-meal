import json
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

URL = "https://dorm.kangwon.ac.kr/bbs/board.php?bo_table=sub02_4"

def clean_lines(cell):
    text = cell.get_text("\n", strip=True)
    return [line.strip() for line in text.splitlines() if line.strip()]

def fetch_meals():
    res = requests.get(URL, timeout=15)
    res.raise_for_status()
    res.encoding = res.apparent_encoding or "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")

    year_match = re.search(r"(20\d{2})\.\s*(\d{1,2})", soup.get_text(" ", strip=True))
    year = int(year_match.group(1)) if year_match else datetime.now().year
    default_month = int(year_match.group(2)) if year_match else datetime.now().month

    meals = {}
    for tr in soup.select("table tr"):
        cols = tr.find_all(["td", "th"])
        if len(cols) < 3:
            continue
        date_text = cols[0].get_text(" ", strip=True)
        m = re.search(r"(\d{1,2})\s*[-/.]\s*(\d{1,2})", date_text)
        if not m:
            continue
        month, day = int(m.group(1)), int(m.group(2))
        actual_year = year + 1 if (default_month == 12 and month == 1) else year
        key = f"{actual_year:04d}-{month:02d}-{day:02d}"

        lunch = clean_lines(cols[1])
        dinner = clean_lines(cols[2])
        if lunch or dinner:
            meals[key] = {"lunch": lunch, "dinner": dinner}

    return meals

if __name__ == "__main__":
    data = fetch_meals()
    with open("meals.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
