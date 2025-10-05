from playwright.sync_api import sync_playwright

class BrowserMgr:
    def __init__(self, cfg):
        self.cfg = cfg
        self._pw = None
        self._browser = None
        self.context = None

    def __enter__(self):
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(
            headless=self.cfg.HEADLESS,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-blink-features=AutomationControlled']
        )
        self.context = self._browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent=self.cfg.USER_AGENT,
            locale='en-US',
            timezone_id=self.cfg.TIMEZONE
        )
        # stealth-ish
        self.context.add_init_script("""            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if self.context:
                self.context.close()
        finally:
            try:
                if self._browser:
                    self._browser.close()
            finally:
                if self._pw:
                    self._pw.stop()
