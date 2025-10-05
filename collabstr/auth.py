from pathlib import Path
from .selectors import USERNAME_INPUT, PASSWORD_INPUT, LOGIN_BUTTON
from .utils import load_cookies, save_cookies, wait_for_cloudflare, log

def _is_logged_in(page) -> bool:
    try:
        if (page.query_selector(".dashboard-menu-holder")
            or page.query_selector(".dashboard-img")
            or page.query_selector("a.header-btn.dashboard-btn")
            or page.query_selector("a[href='/dashboard']")
            or page.query_selector("button:has-text('Logout')")
            or page.query_selector(".profile-avatar")):
            return True
        url = page.url.lower()
        if any(k in url for k in ["/dashboard", "/account", "/home"]):
            return True
        title = (page.title() or "").lower()
        if any(k in title for k in ["dashboard", "account", "profile"]):
            return True
        return False
    except Exception:
        return False

def login_if_needed(context, cfg):
    if not cfg.COLLABSTR_EMAIL or not cfg.COLLABSTR_PASSWORD:
        raise RuntimeError("COLLABSTR_EMAIL/COLLABSTR_PASSWORD missing (see .env).")

    cookie_path = Path(cfg.COOKIES_PATH)
    page = context.new_page()

    # Try cookies
    if load_cookies(context, cookie_path):
        page.goto("https://collabstr.com", wait_until="domcontentloaded", timeout=30000)
        if _is_logged_in(page):
            log.info("Already logged in via cookies.")
            page.close()
            return

    # Fresh login
    page.goto(cfg.LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
    if not wait_for_cloudflare(page):
        page.close()
        raise RuntimeError("Cloudflare/challenge on login page—manual solve needed.")

    page.fill(USERNAME_INPUT, cfg.COLLABSTR_EMAIL, timeout=7000)
    page.fill(PASSWORD_INPUT, cfg.COLLABSTR_PASSWORD, timeout=7000)

    if page.query_selector(LOGIN_BUTTON):
        page.click(LOGIN_BUTTON)
    else:
        page.keyboard.press("Enter")

    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass

    if _is_logged_in(page):
        log.info("Login succeeded.")
        save_cookies(context, cookie_path)
    else:
        raise RuntimeError("Login failed or requires verification (2FA/CAPTCHA).")
    page.close()
