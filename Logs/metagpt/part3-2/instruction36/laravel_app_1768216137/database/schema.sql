-- schema.sql
-- Sample MySQL schema for the Laravel app

-- Create database
CREATE DATABASE IF NOT EXISTS laravel_app_db;
USE laravel_app_db;

-- Create 'users' table
CREATE TABLE IF NOT EXISTS users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert sample users
INSERT INTO users (name, email, password) VALUES
('Alice Smith', 'alice@example.com', '$2y$10$examplehashforalice'),
('Bob Johnson', 'bob@example.com', '$2y$10$examplehashforbob'),
('Charlie Lee', 'charlie@example.com', '$2y$10$examplehashforcharlie'),
('Dana White', 'dana@example.com', '$2y$10$examplehashfordana'),
('Evan Brown', 'evan@example.com', '$2y$10$examplehashforevan');