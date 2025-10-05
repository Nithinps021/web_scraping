import json
import time
import random
import re
from pathlib import Path
from playwright.sync_api import Page
from typing import List
import logging
import re
from rapidfuzz import fuzz, process

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s"
)
log = logging.getLogger("collabstr")

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

def jitter(min_s=1.5, max_s=3.5):
    time.sleep(random.uniform(min_s, max_s))

def extract_emails(text: str) -> List[str]:
    if not text:
        return []
    return list(dict.fromkeys(EMAIL_RE.findall(text)))

def save_cookies(context, path: Path):
    try:
        cookies = context.cookies()
        path.write_text(json.dumps(cookies), encoding="utf-8")
        log.info(f"Saved cookies -> {path}")
    except Exception as e:
        log.warning(f"Failed to save cookies: {e}")

def load_cookies(context, path: Path) -> bool:
    try:
        if not path.exists():
            return False
        cookies = json.loads(path.read_text(encoding="utf-8"))
        context.add_cookies(cookies)
        log.info(f"Loaded cookies from {path}")
        return True
    except Exception as e:
        log.warning(f"Failed to load cookies: {e}")
        return False

def wait_for_cloudflare(page: Page, max_wait=45) -> bool:
    start = time.time()
    while time.time() - start < max_wait:
        try:
            title = page.title()
            if "Just a moment" not in title and "Cloudflare" not in title:
                return True
            if len(page.query_selector_all("div")) > 10:
                return True
        except Exception:
            pass
        time.sleep(1.25)
    return False



BRAND_KEYWORDS = [
    "studio","media","agency","productions","designs","labs","official",
    "channel","team","llc","inc","ltd","pvt","gmbh","plc","co","company","group"
]

def is_brand_like_fuzzy(name: str, threshold: int = 85) -> bool:
    if not name:
        return False
    n = re.sub(r"[\W_]+", " ", name).strip().lower()

    if n.startswith("the "):
        return True
    if re.search(r"\b(" + "|".join(BRAND_KEYWORDS) + r")\b", n):
        return True

    tokens = n.split()
    for t in tokens:
        score = process.extractOne(
            t,
            BRAND_KEYWORDS,
            scorer=fuzz.WRatio   # robust combined scorer
        )
        if score and score[1] >= threshold:
            return True
    return False
