from typing import Optional
from .utils import extract_emails, jitter, log

class InstagramEmailFinder:
    """
    Conservative Instagram email extraction:
    - Try <meta property|name content> set (og:description, description, etc.)
    - Fallback to body innerText
    - Do not login to Instagram (avoid blocks); best-effort only.
    """
    META_SELECT = "meta"

    def __init__(self, cfg, context):
        self.cfg = cfg
        self.context = context

    def try_get_email(self, instagram_url: str) -> Optional[str]:
        ipage = self.context.new_page()
        try:
            ipage.goto(instagram_url, wait_until="domcontentloaded", timeout=45000)
            jitter(3.0, 5.0)

            bio_text = ""
            try:
                metas = ipage.query_selector_all(self.META_SELECT)
                parts = []
                for m in metas:
                    name = (m.get_attribute("name") or m.get_attribute("property") or "").lower()
                    if name in ("description", "og:description", "twitter:description"):
                        c = m.get_attribute("content") or ""
                        if c:
                            parts.append(c)
                bio_text = " ".join(parts)
            except Exception:
                bio_text = ""

            if not bio_text:
                try:
                    bio_text = ipage.inner_text("body", timeout=8000) or ""
                except Exception:
                    bio_text = ""

            emails = extract_emails(bio_text)
            if emails:
                return emails[0]

            return None
        except Exception as e:
            log.warning(f"Instagram fetch error: {e}")
            return None
        finally:
            try:
                ipage.close()
            except:
                pass
