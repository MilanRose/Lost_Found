CREATE DATABASE IF NOT EXISTS lost_found_ai;

USE lost_found_ai;

CREATE TABLE IF NOT EXISTS users (
    id       INT          AUTO_INCREMENT PRIMARY KEY,
    name     VARCHAR(100) NOT NULL,
    reg_no   VARCHAR(20)  UNIQUE NOT NULL,
    email    VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role     VARCHAR(20)  DEFAULT 'student'
);

CREATE TABLE IF NOT EXISTS items (
    id          INT          AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(100),
    description TEXT,
    type        VARCHAR(20),
    category    VARCHAR(50),
    location    VARCHAR(100),
    contact     VARCHAR(100),
    image       VARCHAR(255),
    status      VARCHAR(20)  DEFAULT 'Open',
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    user_id     INT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS claims (
    id          INT  AUTO_INCREMENT PRIMARY KEY,
    item_id     INT,
    claimant_id INT,
    message     TEXT,
    status      VARCHAR(20) DEFAULT 'Pending',
    created_at  TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id)     REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (claimant_id) REFERENCES users(id) ON DELETE CASCADE
);
