-- Create git_checkpoints table
create schema gpu_catalog;
CREATE TABLE gpu_catalog.git_checkpoints (
    id SERIAL PRIMARY KEY,         -- Auto-increment ID for each entry
    last_commit TEXT NOT NULL,     -- Commit hash
    commit_date TIMESTAMP NOT NULL, -- Commit date
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp of entry creation
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Timestamp for any updates
);
