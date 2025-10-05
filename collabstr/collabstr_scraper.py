from typing import List, Tuple, Iterator
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
import time, random

from .models import ListingProfile
from .selectors import LISTING_ITEM, PROFILE_LINK_REL, NAME_ON_PROFILE, INSTAGRAM_LINK
from .utils import log, wait_for_cloudflare, jitter, is_brand_like_fuzzy


def _normalize_profile(href: str) -> str:
    return ("https://collabstr.com" + href) if href and href.startswith("/") else href

class CollabstrListingScraper:
    def __init__(self, cfg, context):
        self.cfg = cfg
        self.context = context
        self._last_first_profile_url: str  = None

    # ---------- helpers ----------
    def _page_url(self, base_url: str, page_num: int) -> str:
        """Return bare START_URL for page 1; append ?pg=N for N>=2."""
        if page_num <= 1:
            return base_url
        parts = urlparse(base_url)
        qs = parse_qs(parts.query)
        qs["pg"] = [str(page_num)]
        new_query = urlencode(qs, doseq=True)
        return urlunparse(parts._replace(query=new_query))

    def _get_listing_items(self, page):
        items = page.query_selector_all(LISTING_ITEM)
        if items:
            return items
        # tolerant fallback
        for s in ("div[class*='profile']", "div[class*='listing']", "div[class*='card']", "a[href*='/']"):
            cand = page.query_selector_all(s)
            if cand and len(cand) > 5:
                return cand
        return []

    def _scrape_page_profiles(self, page_num: int) -> List[ListingProfile]:
        """Fetch a single listing page and return parsed ListingProfile rows."""
        url = self._page_url(self.cfg.START_URL, page_num)
        log.info(f"[list:{page_num}] GET {url}")
        page = self.context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            if not wait_for_cloudflare(page):
                log.warning(f"Cloudflare on listing page {page_num}; results may be partial.")
            jitter(1.0, 1.8)

            items = self._get_listing_items(page)
            if not items:
                # keep a snapshot once for debugging
                if page_num == 1:
                    open("debug_listing.html", "w", encoding="utf-8").write(page.content())
                log.info(f"[list:{page_num}] No items found.")
                return []

            profiles: List[ListingProfile] = []
            for el in items:
                link_el = el.query_selector(PROFILE_LINK_REL)
                if not link_el:
                    continue
                href = link_el.get_attribute("href")
                if not href:
                    continue
                prof_url = _normalize_profile(href)
                username = href.strip("/").split("/")[-1]
                profiles.append(ListingProfile(username=username, profile_url=prof_url))

            # duplicate-page guard: if first profile matches previous page, skip ahead
            if profiles:
                first_url = profiles[0].profile_url
                if self._last_first_profile_url == first_url:
                    log.warning(f"[list:{page_num}] Looks identical to previous page (first card = {first_url}). "
                                f"Will attempt to skip to next page.")
                    # mark as empty so caller advances page_num again
                    return []
                self._last_first_profile_url = first_url

            log.info(f"[list:{page_num}] Parsed {len(profiles)} cards.")
            return profiles
        finally:
            try:
                page.close()
            except:
                pass

    def get_profiles(self, batch_size: int = 50, start_page: int = 1, max_pages: int = None) -> Iterator[List[ListingProfile]]:
        """
        Yield batches of profiles (≈ batch_size each).
        Each batch is produced by visiting as many pages as needed to fill it.
        The next iteration continues from the next page.
        """
        assert batch_size > 0, "batch_size must be > 0"
        page_num = start_page
        pages_seen = 0

        while True:
            if max_pages is not None and pages_seen >= max_pages:
                return

            batch: List[ListingProfile] = []

            while len(batch) < batch_size:
                if max_pages is not None and pages_seen >= max_pages:
                    break

                page_rows = self._scrape_page_profiles(page_num)
                # if page returns empty, assume no more results (or duplicate); advance and try once
                if not page_rows:
                    page_num += 1
                    pages_seen += 1
                    # optional small sleep to avoid hammering
                    jitter(0.4, 0.8)
                    # try the next page; if max_pages hit, outer loop will stop
                    # to continue the while to see if we can fill the batch
                    if max_pages is not None and pages_seen >= max_pages:
                        break
                    # we don't break yet; attempt to fill a remainder from future pages
                    continue

                batch.extend(page_rows)
                page_num += 1
                pages_seen += 1
                jitter(0.6, 1.2)

                # safety: if the site shows huge pages, we still respect batch size
                if len(batch) >= batch_size:
                    break

            if not batch:
                return

            # exact size
            if len(batch) > batch_size:
                batch = batch[:batch_size]

            yield batch

    def get_profile_details(self, profile_url: str) -> Tuple[str, str]:
        p = self.context.new_page()
        p.goto(profile_url, wait_until="domcontentloaded", timeout=60000)
        if not wait_for_cloudflare(p):
            log.warning("Cloudflare on profile page—skipping extras.")
        jitter(1.0, 1.8)

        name = ""
        n = p.query_selector(NAME_ON_PROFILE)
        if n:
            try:
                name = (n.inner_text() or "").strip()
            except:
                name = ""
        if is_brand_like_fuzzy(name):
            p.close()
            return None, None

        insta = ""
        link = p.query_selector(INSTAGRAM_LINK)
        if link:
            insta = link.get_attribute("href") or ""

        p.close()
        return name, insta
