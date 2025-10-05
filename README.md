# Collabstr → Instagram Email Scraper (Playwright)

A **modular, scalable** project that:  
1. Logs into Collabstr (with cookie persistence).  
2. Scrapes profile cards.  
3. Visits each profile to grab Instagram.  
4. Attempts to parse an email from Instagram meta/description.  
5. Saves all results to CSV.  

---

## 🔧 Tools and Approach Used
- **Playwright (Python)** → automated browsing, scraping, and login handling.  
- **dotenv** → manage secrets/config (`.env` file for credentials & toggles).  
- **CSV Writer** → structured data export.  
- **Regex parsing** → extract email addresses from Instagram bios and meta tags.  
- **Modular design** → separate scraper modules (`collabstr_scraper.py`, `instagram_scraper.py`, etc.) for easy extension.  

---

## ⚡ Challenges Faced & Solutions
- **Login persistence** → Solved by saving and reusing cookies (`collabstr_cookies.json`).  
- **Dynamic UI changes (selectors)** → Multiple fallbacks for selectors (`meta`, `body`, `bio`).  
- **Anti-bot detection on Instagram** → Randomized sleeps, natural navigation, and optional non-headless mode.  
- **Missing emails** → Fallback parsing of `meta` tags and body text.  

---

## ✅ Data Validation Steps
- **Regex filtering** → ensures valid email format.  
- **Deduplication** → avoids duplicate entries.  
- **Role tagging** → saves each entry with `role_type` (e.g., UGC, Video).  
- **Fail-safe CSV writing** → ensures partial data is saved even if execution stops midway.  

---

## ⏱️ Estimated Time Spent
- Setup & environment config: ~1 hour  
- Playwright login + cookie handling: ~2 hours  
- Collabstr listing & profile scraping: ~2 hours  
- Instagram email extraction logic: ~3 hours  
- Data validation & CSV writing: ~1 hour  
- **Total: ~9 hours** end-to-end  

---

## 📈 Scalability (1,000+ Profiles)
- **Batch processing** → configurable `MAX_ITEMS` per run.  
- **Headless mode** → faster execution with reduced overhead.  
- **Cookie reuse** → avoids repeated logins.  
- **Rate-limiting (sleep jitter)** → reduces blocking risk.  
- **Modular extension** → easily add new sources (e.g., Behance, Shoutt) by adding new scrapers.  

---

## 🚀 Setup

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
cp .env.example .env
# Fill COLLABSTR_EMAIL & COLLABSTR_PASSWORD in .env
