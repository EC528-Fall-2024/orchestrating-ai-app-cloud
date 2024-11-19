-- Create and select the database
CREATE DATABASE IF NOT EXISTS logs;
USE logs;

-- Create the logs table
CREATE TABLE logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    run_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    path_to_data VARCHAR(255) NOT NULL,
    path_to_src VARCHAR(255) NOT NULL,
    path_to_output VARCHAR(255) NOT NULL,
    state VARCHAR(20) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    compute_instance VARCHAR(255),
    CONSTRAINT valid_state CHECK (state IN ('DEPLOYING', 'ACTIVE', 'DEAD'))
);

-- Create an index on run_id for faster lookups
CREATE INDEX idx_run_id ON logs(run_id);

-- Create an index on user_id for faster lookups
CREATE INDEX idx_user_id ON logs(user_id);

-- Create an index on state for faster filtering
CREATE INDEX idx_state ON logs(state);
