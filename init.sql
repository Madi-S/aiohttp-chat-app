CREATE DATABASE IF NOT EXISTS webchat;
USE webchat;
CREATE table IF NOT EXISTS chat_users(
    id serial,
    username VARCHAR(21) NOT NULL,
    pwd VARCHAR(31) NOT NULL,
    pwd_reset_token VARCHAR(100),
    pwd_reset_expiration DATETIME
);
INSERT INTO chat_users(username, pwd)
VALUES ('KumysPower', 'KumysSila123'),
    ('Jeremy34', '040204Johnson'),
    ('Danielzzz', 'easyPASSSWORD555'),
    ('AttilaJohnson', 'aJ5435345345'),
    ('FuckingCow', 'FuckingCow123');