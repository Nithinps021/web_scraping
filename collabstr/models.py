from dataclasses import dataclass

@dataclass
class ListingProfile:
    username: str
    profile_url: str

@dataclass
class CreatorRow:
    name: str
    email: str
    profile_link: str
    role_type: str
