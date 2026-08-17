from pathlib import Path
from datetime import date, timedelta
import csv
import random

from faker import Faker


# ============================================================
# Configuration
# ============================================================

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

fake = Faker()

# Fixed seed = reproducible synthetic dataset
SEED = 42

random.seed(SEED)
Faker.seed(SEED)

NUM_CUSTOMERS = 50

SEGMENTS = ["SMB", "Mid-Market", "Enterprise"]

SEGMENT_WEIGHTS = [40, 35, 25]

ACCOUNT_MANAGERS_PER_SEGMENT = {
    "SMB": 2,
    "Mid-Market": 2,
    "Enterprise": 2,
}

USER_COUNT_RANGES = {
    "SMB": (3, 12),
    "Mid-Market": (10, 30),
    "Enterprise": (25, 75),
}

EMPLOYEE_COUNT_RANGES = {
    "SMB": (20, 199),
    "Mid-Market": (200, 999),
    "Enterprise": (1000, 5000),
}

ACV_RANGES = {
    "SMB": (5_000, 25_000),
    "Mid-Market": (25_000, 100_000),
    "Enterprise": (100_000, 500_000),
}

PLANS = {
    "SMB": ["Starter", "Growth"],
    "Mid-Market": ["Growth", "Professional"],
    "Enterprise": ["Professional", "Enterprise"],
}

HEALTH_SCENARIOS = [
    "Healthy",
    "Watch",
    "At Risk",
]

HEALTH_WEIGHTS = [
    60,
    25,
    15,
]

USER_ROLES = [
    "Admin",
    "Manager",
    "Analyst",
    "User",
]

EVENT_TYPES = [
    "login",
    "dashboard_view",
    "report_created",
    "export",
    "integration_used",
]

PAYMENT_STATUSES = [
    "Paid",
    "Late",
    "Failed",
]

TODAY = date.today()


# ============================================================
# Helper function for writing CSV files
# ============================================================

def write_csv(filename, rows, fieldnames):
    output_file = DATA_DIR / filename

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    print(
        f"Created {output_file} "
        f"({len(rows)} rows)"
    )


# ============================================================
# Generate account managers
# ============================================================

account_managers = []

manager_ids_by_segment = {
    segment: []
    for segment in SEGMENTS
}

account_manager_id = 1

for segment in SEGMENTS:

    manager_count = (
        ACCOUNT_MANAGERS_PER_SEGMENT[segment]
    )

    for _ in range(manager_count):

        name = fake.unique.name()
        email = fake.unique.company_email()

        account_managers.append(
            {
                "account_manager_id": account_manager_id,
                "name": name,
                "email": email,
                "team": segment,
            }
        )

        manager_ids_by_segment[
            segment
        ].append(account_manager_id)

        account_manager_id += 1


write_csv(
    "account_managers.csv",
    account_managers,
    [
        "account_manager_id",
        "name",
        "email",
        "team",
    ],
)


# ============================================================
# Generate customers
# ============================================================

customers = []

for customer_id in range(
    1,
    NUM_CUSTOMERS + 1,
):

    segment = random.choices(
        SEGMENTS,
        weights=SEGMENT_WEIGHTS,
        k=1,
    )[0]

    employee_min, employee_max = (
        EMPLOYEE_COUNT_RANGES[segment]
    )

    employee_count = random.randint(
        employee_min,
        employee_max,
    )

    acv_min, acv_max = (
        ACV_RANGES[segment]
    )

    annual_contract_value = round(
        random.uniform(
            acv_min,
            acv_max,
        ),
        2,
    )

    account_manager_id = random.choice(
        manager_ids_by_segment[segment]
    )

    customers.append(
        {
            "customer_id": customer_id,
            "company_name": fake.unique.company(),
            "industry": fake.job(),
            "employee_count": employee_count,
            "segment": segment,
            "annual_contract_value": annual_contract_value,
            "account_manager_id": account_manager_id,
        }
    )


write_csv(
    "customers.csv",
    customers,
    [
        "customer_id",
        "company_name",
        "industry",
        "employee_count",
        "segment",
        "annual_contract_value",
        "account_manager_id",
    ],
)


# ============================================================
# Assign hidden customer-health scenarios
# ============================================================

health_scenarios = {}

for customer in customers:

    customer_id = customer["customer_id"]

    health_scenarios[
        customer_id
    ] = random.choices(
        HEALTH_SCENARIOS,
        weights=HEALTH_WEIGHTS,
        k=1,
    )[0]


# ============================================================
# Generate users
# ============================================================

users = []

users_by_customer = {}

user_id = 1

for customer in customers:

    customer_id = customer["customer_id"]
    segment = customer["segment"]

    min_users, max_users = (
        USER_COUNT_RANGES[segment]
    )

    num_users = random.randint(
        min_users,
        max_users,
    )

    users_by_customer[
        customer_id
    ] = []

    for _ in range(num_users):

        name = fake.name()
        email = fake.unique.email()

        user = {
            "user_id": user_id,
            "customer_id": customer_id,
            "name": name,
            "email": email,
            "role": random.choice(
                USER_ROLES
            ),
        }

        users.append(user)

        users_by_customer[
            customer_id
        ].append(user)

        user_id += 1


write_csv(
    "users.csv",
    users,
    [
        "user_id",
        "customer_id",
        "name",
        "email",
        "role",
    ],
)


# ============================================================
# Generate subscriptions
# ============================================================

subscriptions = []

subscription_id = 1

for customer in customers:

    customer_id = customer["customer_id"]
    segment = customer["segment"]

    scenario = health_scenarios[
        customer_id
    ]

    contract_start_date = (
        TODAY
        - timedelta(
            days=random.randint(
                90,
                1000,
            )
        )
    )

    if scenario == "At Risk":

        days_until_renewal = (
            random.randint(
                10,
                120,
            )
        )

    elif scenario == "Watch":

        days_until_renewal = (
            random.randint(
                60,
                250,
            )
        )

    else:

        days_until_renewal = (
            random.randint(
                120,
                500,
            )
        )

    renewal_date = (
        TODAY
        + timedelta(
            days=days_until_renewal
        )
    )

    if scenario == "At Risk":
        status = "At Risk"
    else:
        status = "Active"

    subscriptions.append(
        {
            "subscription_id": subscription_id,
            "customer_id": customer_id,
            "plan": random.choice(
                PLANS[segment]
            ),
            "annual_contract_value": (
                customer[
                    "annual_contract_value"
                ]
            ),
            "contract_start_date": (
                contract_start_date.isoformat()
            ),
            "renewal_date": (
                renewal_date.isoformat()
            ),
            "status": status,
        }
    )

    subscription_id += 1


write_csv(
    "subscriptions.csv",
    subscriptions,
    [
        "subscription_id",
        "customer_id",
        "plan",
        "annual_contract_value",
        "contract_start_date",
        "renewal_date",
        "status",
    ],
)


# ============================================================
# Generate usage events
# ============================================================

usage_events = []

event_id = 1

for customer in customers:

    customer_id = customer["customer_id"]

    scenario = health_scenarios[
        customer_id
    ]

    customer_users = (
        users_by_customer[
            customer_id
        ]
    )

    # Six months of product usage.
    # Oldest month is first.
    # Newest month is last.

    if scenario == "Healthy":

        monthly_event_ranges = [
            (35, 50),
            (35, 50),
            (40, 55),
            (40, 55),
            (45, 60),
            (45, 60),
        ]

    elif scenario == "Watch":

        monthly_event_ranges = [
            (45, 60),
            (40, 55),
            (35, 50),
            (30, 45),
            (25, 40),
            (20, 35),
        ]

    else:

        monthly_event_ranges = [
            (60, 80),
            (55, 75),
            (40, 60),
            (25, 45),
            (15, 30),
            (5, 15),
        ]

    for month_index, event_range in enumerate(
        monthly_event_ranges
    ):

        min_events, max_events = (
            event_range
        )

        num_events = random.randint(
            min_events,
            max_events,
        )

        # month_index = 0 is the oldest month
        # month_index = 5 is the newest month

        days_ago_start = (
            5 - month_index
        ) * 30

        days_ago_end = (
            days_ago_start + 29
        )

        for _ in range(num_events):

            user = random.choice(
                customer_users
            )

            event_date = (
                TODAY
                - timedelta(
                    days=random.randint(
                        days_ago_start,
                        days_ago_end,
                    )
                )
            )

            usage_events.append(
                {
                    "event_id": event_id,
                    "customer_id": customer_id,
                    "user_id": user["user_id"],
                    "event_type": random.choice(
                        EVENT_TYPES
                    ),
                    "event_date": event_date.isoformat(),
                }
            )

            event_id += 1


write_csv(
    "usage_events.csv",
    usage_events,
    [
        "event_id",
        "customer_id",
        "user_id",
        "event_type",
        "event_date",
    ],
)


# ============================================================
# Generate support tickets
# ============================================================

support_tickets = []

ticket_id = 1

for customer in customers:

    customer_id = customer["customer_id"]

    scenario = health_scenarios[
        customer_id
    ]

    if scenario == "Healthy":

        num_tickets = random.randint(
            0,
            4,
        )

        severity_weights = [
            70,
            25,
            5,
        ]

        status_weights = [
            90,
            10,
        ]

    elif scenario == "Watch":

        num_tickets = random.randint(
            3,
            8,
        )

        severity_weights = [
            40,
            45,
            15,
        ]

        status_weights = [
            65,
            35,
        ]

    else:

        num_tickets = random.randint(
            7,
            15,
        )

        severity_weights = [
            20,
            45,
            35,
        ]

        status_weights = [
            45,
            55,
        ]

    for _ in range(num_tickets):

        severity = random.choices(
            [
                "Low",
                "Medium",
                "High",
            ],
            weights=severity_weights,
            k=1,
        )[0]

        status = random.choices(
            [
                "Resolved",
                "Open",
            ],
            weights=status_weights,
            k=1,
        )[0]

        created_date = (
            TODAY
            - timedelta(
                days=random.randint(
                    0,
                    180,
                )
            )
        )

        support_tickets.append(
            {
                "ticket_id": ticket_id,
                "customer_id": customer_id,
                "subject": fake.sentence(
                    nb_words=random.randint(
                        4,
                        8,
                    )
                ).rstrip("."),
                "description": fake.paragraph(
                    nb_sentences=random.randint(
                        2,
                        5,
                    )
                ),
                "severity": severity,
                "status": status,
                "created_date": (
                    created_date.isoformat()
                ),
            }
        )

        ticket_id += 1


write_csv(
    "support_tickets.csv",
    support_tickets,
    [
        "ticket_id",
        "customer_id",
        "subject",
        "description",
        "severity",
        "status",
        "created_date",
    ],
)


# ============================================================
# Generate payments
# ============================================================

payments = []

payment_id = 1

for customer in customers:

    customer_id = customer["customer_id"]

    scenario = health_scenarios[
        customer_id
    ]

    monthly_value = round(
        customer[
            "annual_contract_value"
        ] / 12,
        2,
    )

    # Generate six months of payment history

    for months_ago in range(6):

        payment_date = (
            TODAY
            - timedelta(
                days=months_ago * 30
            )
        )

        if scenario == "Healthy":

            payment_weights = [
                96,
                4,
                0,
            ]

        elif scenario == "Watch":

            payment_weights = [
                80,
                18,
                2,
            ]

        else:

            payment_weights = [
                55,
                30,
                15,
            ]

        payment_status = (
            random.choices(
                PAYMENT_STATUSES,
                weights=payment_weights,
                k=1,
            )[0]
        )

        payments.append(
            {
                "payment_id": payment_id,
                "customer_id": customer_id,
                "amount": monthly_value,
                "payment_date": (
                    payment_date.isoformat()
                ),
                "status": payment_status,
            }
        )

        payment_id += 1


write_csv(
    "payments.csv",
    payments,
    [
        "payment_id",
        "customer_id",
        "amount",
        "payment_date",
        "status",
    ],
)


# ============================================================
# Summary
# ============================================================

print()
print(
    "Synthetic data generation complete."
)

print(
    f"Account managers: "
    f"{len(account_managers)}"
)

print(
    f"Customers: "
    f"{len(customers)}"
)

print(
    f"Users: "
    f"{len(users)}"
)

print(
    f"Subscriptions: "
    f"{len(subscriptions)}"
)

print(
    f"Usage events: "
    f"{len(usage_events)}"
)

print(
    f"Support tickets: "
    f"{len(support_tickets)}"
)

print(
    f"Payments: "
    f"{len(payments)}"
)