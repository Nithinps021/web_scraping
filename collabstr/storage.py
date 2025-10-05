import csv
import os
from .models import CreatorRow

class CsvWriter:
    def __init__(self, path: str):
        self.path = path
        file_exists = os.path.exists(self.path)
        if not file_exists:
            with open(self.path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f, fieldnames=["name", "email", "profile_link", "role_type"]
                )
                writer.writeheader()

    def write(self, r: CreatorRow) -> None:
        with open(self.path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=["name", "email", "profile_link", "role_type"]
            )
            writer.writerow({
                "name": r.name,
                "email": r.email,
                "profile_link": r.profile_link,
                "role_type": r.role_type
            })
        print("Wrote to csv")
