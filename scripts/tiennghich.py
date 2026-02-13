import requests
from bs4 import BeautifulSoup
import time
import json

BASE_URL = "https://truyenfull.vision/tien-nghich"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}

all_chapters = []

def crawl_page(page: int):
    if page == 1:
        url = f"{BASE_URL}/#list-chapter"
    else:
        url = f"{BASE_URL}/trang-{page}/#list-chapter"

    print(f"🔎 Crawling: {url}")
    res = requests.get(url, headers=HEADERS, timeout=15)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select("#list-chapter ul.list-chapter li a")

    chapters = []

    for a in items:
        text = a.get_text(strip=True)
        href = a.get("href")

        # Ví dụ text: "1: Ly hương" hoặc "Chương 1: Ly hương"
        text = text.replace("Chương", "").strip()

        try:
            number_str, title = text.split(":", 1)
            number = int(number_str.strip())
            title = title.strip()
        except:
            continue

        chapters.append({
            "number": number,
            "title": title,
            "url": href
        })

    return chapters

def get_total_pages():
    res = requests.get(f"{BASE_URL}/#list-chapter", headers=HEADERS, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")
    total_page_input = soup.select_one("#total-page")
    return int(total_page_input["value"])

def main():
    total_pages = get_total_pages()
    print(f"📘 Tổng số trang: {total_pages}")

    for page in range(1, total_pages + 1):
        chapters = crawl_page(page)
        all_chapters.extend(chapters)
        time.sleep(0.8)  # chống bị chặn IP

    # Sort theo số chương
    all_chapters.sort(key=lambda x: x["number"])

    # Lưu ra file JSON
    with open("tien_nghich_chapters.json", "w", encoding="utf-8") as f:
        json.dump(all_chapters, f, ensure_ascii=False, indent=2)

    print(f"✅ Đã crawl xong {len(all_chapters)} chương")
    print("📁 File lưu: tien_nghich_chapters.json")

if __name__ == "__main__":
    main()
