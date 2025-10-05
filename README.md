# Collabstr → Instagram email scraper (Playwright)

Modular, scalable project that:
1) Logs into Collabstr (with cookie persistence),
2) Scrapes profile cards,
3) Visits each profile to grab Instagram,
4) Tries to parse an email from Instagram meta/description,
5) Saves to CSV.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
cp .env.example .env
# fill COLLABSTR_EMAIL & COLLABSTR_PASSWORD in .env
```

## Run

```bash
python run.py
```

CSV path controlled via `OUTPUT_CSV` in `.env`.

## Config

All toggles in `.env`:
- `HEADLESS=false|true`
- `MAX_ITEMS=10`
- `ROLE_TYPE=UGC`
- `COOKIES_PATH=collabstr_cookies.json`
- etc.

## Notes

- Respect target sites' Terms of Service, robots, and rate limits.
- Instagram layout, anti-bot, or geo can affect extraction; this script uses best-effort meta/body parsing without login.
- To extend storage (e.g., Postgres/NDJSON), add a new writer in `storage.py`.
- To add more sources, add a new `X_scraper.py` and plug it into `run.py`.

