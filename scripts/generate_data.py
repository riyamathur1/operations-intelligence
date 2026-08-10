from pathlib import Path
import csv

DATA_DIR = Path("data")

account_managers = [
    {
        "account_manager_id": 1,
        "name": "Sarah Lee",
        "email": "sarah.lee@fictionalsoftware.com",
        "team": "Mid-Market",
    },
    {
        "account_manager_id": 2,
        "name": "Marcus Chen",
        "email": "marcus.chen@fictionalsoftware.com",
        "team": "Enterprise",
    },
    {
        "account_manager_id": 3,
        "name": "Priya Patel",
        "email": "priya.patel@fictionalsoftware.com",
        "team": "SMB",
    },
]

output_file = DATA_DIR / "account_managers.csv"

with output_file.open("w", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "account_manager_id",
            "name",
            "email",
            "team",
        ],
    )

    writer.writeheader()
    writer.writerows(account_managers)

print(f"Created {output_file}")