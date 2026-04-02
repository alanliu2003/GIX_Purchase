-- GIX team purchase tracking — run via init_db.py against your MySQL server
CREATE TABLE IF NOT EXISTS teams (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    team_number INT NOT NULL UNIQUE,
    budget_remaining DECIMAL(12, 2) NOT NULL DEFAULT 200.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS purchases (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    team_id INT UNSIGNED NOT NULL,
    cfo_name VARCHAR(255) NOT NULL,
    purchase_link TEXT NOT NULL,
    price_per_item DECIMAL(12, 2) NOT NULL,
    quantity INT UNSIGNED NOT NULL,
    notes TEXT,
    instructor_approved TINYINT(1) NOT NULL DEFAULT 0,
    status ENUM('under_process', 'arrived', 'problematic') NOT NULL DEFAULT 'under_process',
    deducted TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    INDEX idx_purchases_team (team_id),
    INDEX idx_purchases_status (status)
);
