-- Create reports table
CREATE TABLE IF NOT EXISTS reports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    report_type ENUM('user_progress', 'learning_analytics', 'ai_usage', 'monthly_summary', 'custom_report') NOT NULL,
    title VARCHAR(255) NOT NULL,
    format ENUM('pdf', 'excel', 'csv') NOT NULL,
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending' NOT NULL,
    parameters JSON NOT NULL,
    file_path VARCHAR(500),
    file_size INT,
    error_message TEXT,
    created_by INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at DATETIME,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_reports_status (status),
    INDEX idx_reports_created_by (created_by),
    INDEX idx_reports_created_at (created_at)
);