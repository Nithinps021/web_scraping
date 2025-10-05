import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass(frozen=True)
class Settings:
    START_URL: str
    LOGIN_URL: str
    COOKIES_PATH: str
    OUTPUT_CSV: str
    COLLABSTR_EMAIL: str
    COLLABSTR_PASSWORD: str
    HEADLESS: bool
    TIMEZONE: str
    ROLE_TYPE: str

    USER_AGENT: str = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36")

    @staticmethod
    def _bool(v: str, default: bool) -> bool:
        if v is None:
            return default
        return v.lower() in ("1", "true", "yes", "y")

    @classmethod
    def ugc_config_load(cls) -> "Settings":
        load_dotenv(override=False)
        return cls(
            START_URL=os.getenv("START_URL", "https://collabstr.com/influencers?c=UGC"),
            LOGIN_URL=os.getenv("LOGIN_URL", "https://collabstr.com/login"),
            COOKIES_PATH=os.getenv("COOKIES_PATH", "collabstr_cookies.json"),
            OUTPUT_CSV=os.getenv("OUTPUT_CSV", "ucg_creators_list.csv"),
            COLLABSTR_EMAIL=os.getenv("COLLABSTR_EMAIL", ""),
            COLLABSTR_PASSWORD=os.getenv("COLLABSTR_PASSWORD", ""),
            HEADLESS=cls._bool(os.getenv("HEADLESS", "false"), False),
            TIMEZONE=os.getenv("TIMEZONE", "America/New_York"),
            ROLE_TYPE=os.getenv("ROLE_TYPE", "UGC"),
        )
    
    @classmethod
    def video_config_load(cls) -> "Settings":
        load_dotenv(override=False)
        return cls(
            START_URL=os.getenv("START_URL", "https://collabstr.com/influencers?c=video+editor"),
            LOGIN_URL=os.getenv("LOGIN_URL", "https://collabstr.com/login"),
            COOKIES_PATH=os.getenv("COOKIES_PATH", "collabstr_cookies.json"),
            OUTPUT_CSV=os.getenv("OUTPUT_CSV", "video_editors_list.csv"),
            COLLABSTR_EMAIL=os.getenv("COLLABSTR_EMAIL", "coldstart021@gmail.com"),
            COLLABSTR_PASSWORD=os.getenv("COLLABSTR_PASSWORD", "@Supernova123"),
            HEADLESS=cls._bool(os.getenv("HEADLESS", "false"), False),
            TIMEZONE=os.getenv("TIMEZONE", "America/New_York"),
            ROLE_TYPE=os.getenv("ROLE_TYPE", "Video Editor"),
        )

