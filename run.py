from concurrent.futures import ProcessPoolExecutor
from multiprocessing import set_start_method

from collabstr.config import Settings
from collabstr.browser import BrowserMgr
from collabstr.auth import login_if_needed
from collabstr.collabstr_scraper import CollabstrListingScraper
from collabstr.instagram_scraper import InstagramEmailFinder
from collabstr.storage import CsvWriter
from collabstr.models import CreatorRow

from collabstr.utils import log
import random, time

def scrap_content(cfg):
    batch_size     = getattr(cfg, "BATCH_SIZE", 50)
    target_emails  = getattr(cfg, "TARGET_EMAIL_COUNT", 50)
    max_pages      = getattr(cfg, "MAX_PAGES", 50)
    sleep_min      = getattr(cfg, "REQUEST_SLEEP_MIN", 0.8)
    sleep_max      = getattr(cfg, "REQUEST_SLEEP_MAX", 1.6)

    log.info("Booting browser...")
    with BrowserMgr(cfg) as bm:
        context = bm.context
        login_if_needed(context, cfg)

        listing = CollabstrListingScraper(cfg, context)
        ig      = InstagramEmailFinder(cfg, context)
        writer  = CsvWriter(cfg.OUTPUT_CSV)

        total_with_email = 0
        processed_total  = 0
        seen_urls        = set()

        for batch_idx, batch in enumerate(
            listing.get_profiles(batch_size=batch_size, start_page=1, max_pages=max_pages),
            start=1
        ):
            if target_emails and total_with_email >= target_emails:
                break

            log.info(f"[Batch {batch_idx}] Received {len(batch)} profiles")

            for i, lp in enumerate(batch, start=1):
                if target_emails and total_with_email >= target_emails:
                    break

                if lp.profile_url in seen_urls:
                    continue
                seen_urls.add(lp.profile_url)
                processed_total += 1

                log.info(f"[Batch {batch_idx} • {i}/{len(batch)}] {lp.profile_url}")

                try:
                    name, insta_url = listing.get_profile_details(lp.profile_url)
                    if not name:
                        continue
                except Exception as e:
                    log.warning(f"Profile details failed: {e}")
                    continue

                email = ""
                if insta_url:
                    try:
                        email = ig.try_get_email(insta_url) or ""
                    except Exception as e:
                        log.warning(f"Instagram fetch failed: {e}")

                row = CreatorRow(
                    name=name or lp.username or "",
                    email=email or "",
                    profile_link=lp.profile_url,
                    role_type=cfg.ROLE_TYPE
                )
                if email:
                    writer.write(row)
                    total_with_email += 1
                    log.info(f"✓ email found ({total_with_email}/{target_emails}) — {email}")

                time.sleep(random.uniform(sleep_min, sleep_max))

            if total_with_email == target_emails:
                break

        if total_with_email == 0:
            log.warning("Finished with 0 emails found (rows still written).")
        else:
            log.info(f"Finished. Emails found: {total_with_email}  | Output: {cfg.OUTPUT_CSV}")

def worker(which: str):
    cfg = Settings.ugc_config_load() if which == "ugc" else Settings.video_config_load()
    return scrap_content(cfg)

if __name__ == "__main__":
    try:
        set_start_method("spawn")
    except RuntimeError:
        pass
    with ProcessPoolExecutor(max_workers=2) as ex:
        list(ex.map(worker, ["ugc", "video"]))