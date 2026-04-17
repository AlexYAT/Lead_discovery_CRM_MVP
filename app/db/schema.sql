PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    profile_name TEXT NOT NULL,
    profile_url TEXT NOT NULL,
    source_url TEXT,
    source_text TEXT,
    detected_theme TEXT,
    score REAL,
    status TEXT NOT NULL DEFAULT 'new',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contact_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER NOT NULL,
    date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    message_text TEXT,
    outcome TEXT,
    next_action TEXT,
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS consultations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER NOT NULL,
    planned_at TEXT NOT NULL,
    status TEXT NOT NULL,
    result TEXT,
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_contact_attempts_lead_id
    ON contact_attempts (lead_id);

CREATE INDEX IF NOT EXISTS idx_consultations_lead_id
    ON consultations (lead_id);
