-- Set charset
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET character_set_connection=utf8mb4;

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS magic7 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE magic7;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    job_title VARCHAR(100),
    department VARCHAR(100),
    ai_level ENUM('beginner', 'intermediate', 'advanced', 'expert') DEFAULT 'beginner',
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_id VARCHAR(36) NOT NULL,
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    role ENUM('user', 'assistant', 'system') NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    INDEX idx_conversation_id (conversation_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create learning_paths table
CREATE TABLE IF NOT EXISTS learning_paths (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    job_category VARCHAR(100) NOT NULL,
    current_level INT DEFAULT 1,
    progress DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create ai_tools table
CREATE TABLE IF NOT EXISTS ai_tools (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    difficulty ENUM('basic', 'intermediate', 'advanced') NOT NULL,
    description TEXT,
    usage_guide TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_difficulty (difficulty)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert sample AI tools
INSERT INTO ai_tools (name, category, difficulty, description, usage_guide) VALUES
('ChatGPT', '텍스트 생성', 'basic', 'OpenAI의 대화형 AI 도구로 텍스트 생성, 번역, 요약 등 다양한 작업 수행', '1. 명확한 프롬프트 작성\n2. 컨텍스트 제공\n3. 반복적인 개선'),
('Midjourney', '이미지 생성', 'intermediate', 'AI 기반 이미지 생성 도구로 텍스트 설명을 통해 고품질 이미지 생성', '1. Discord 가입\n2. /imagine 명령어 사용\n3. 프롬프트 작성'),
('GitHub Copilot', '코드 생성', 'intermediate', '개발자를 위한 AI 코딩 어시스턴트', '1. VS Code 확장 설치\n2. 주석으로 의도 설명\n3. Tab으로 제안 수락'),
('Notion AI', '문서 작성', 'basic', 'Notion 내장 AI로 문서 작성, 요약, 번역 지원', '1. 스페이스바 입력\n2. AI 명령 선택\n3. 결과 편집');

-- Create test users
INSERT INTO users (email, password_hash, name, job_title, department, ai_level) VALUES
('test@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '김현준', '마케팅 매니저', '마케팅팀', 'intermediate'),
('user2@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '이서연', '기획자', '전략기획팀', 'beginner'),
('user3@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '박지혜', '영업 대리', '영업팀', 'beginner');

-- Note: Default password for test users is 'secret'