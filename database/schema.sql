CREATE TABLE IF NOT EXISTS account_managers (
    account_manager_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    team VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    industry VARCHAR(100),
    plan VARCHAR(50),
    monthly_revenue DECIMAL(10, 2),
    contract_start_date DATE,
    renewal_date DATE,
    licensed_users INTEGER,
    created_at TIMESTAMP NOT NULL,
    account_manager_id INTEGER,
    FOREIGN KEY (account_manager_id)
        REFERENCES account_managers(account_manager_id)
);

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    email VARCHAR(150) NOT NULL,
    role VARCHAR(50),
    signup_date DATE NOT NULL,
    is_active BOOLEAN NOT NULL,
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),
    UNIQUE (customer_id, email)
);

CREATE TABLE IF NOT EXISTS product_usage (
    usage_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    usage_date DATE NOT NULL,
    login_count INTEGER NOT NULL DEFAULT 0,
    workflows_created INTEGER NOT NULL DEFAULT 0,
    tasks_completed INTEGER NOT NULL DEFAULT 0,
    reports_viewed INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id)
        REFERENCES users(user_id),
    UNIQUE (user_id, usage_date)
);

CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    priority VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    category VARCHAR(50),
    resolved_at TIMESTAMP,
    satisfaction_score INTEGER,
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),
    CHECK (
        satisfaction_score IS NULL
        OR satisfaction_score BETWEEN 1 AND 5
    )
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY,
    invoice_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    billing_period VARCHAR(7) NOT NULL,
    payment_date DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    payment_method VARCHAR(30),
    failure_reason VARCHAR(100),
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);