import os
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PublicCaseScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def scrape_jusbrasil_or_public(self, url_or_path: str) -> str:
        # Check if the target is a local file on disk
        if os.path.exists(url_or_path):
            print(f"[DEBUG] Reading from local file: {url_or_path}")
            with open(url_or_path, "r", encoding="utf-8", errors="ignore") as f:
                html_content = f.read()
        else:
            try:
                response = requests.get(url_or_path, headers=self.headers, timeout=15, verify=False)
                response.raise_for_status()
                html_content = response.text
            except Exception as e:
                print(f"[ERROR] Falha ao fazer o scraping da URL {url_or_path}: {e}")
                return ""

        soup = BeautifulSoup(html_content, "html.parser")
        
        # Extract text from standard structured elements (tables, list items, paragraphs)
        movements = soup.find_all(["tr", "li", "p", "div"])

        extracted_text = []
        for mov in movements:
            text = " ".join(mov.get_text(separator=" ", strip=True).split())
            # Keep text blocks long enough to contain legal movement info
            if text and len(text) > 25: 
                extracted_text.append(text)

        # Deduplicate redundant lines caused by nested HTML tags
        extracted_text = list(dict.fromkeys(extracted_text))

        return "\n".join(extracted_text)
