DROP TABLE IF EXISTS jobs;

CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    position TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Applied', 'Interviewed', 'Declined', 'Accepted')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_company ON jobs(company);
CREATE INDEX idx_jobs_position ON jobs(position);
CREATE INDEX idx_jobs_last_modified ON jobs(last_modified);