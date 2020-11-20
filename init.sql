CREATE DATABASE IF NOT EXISTS webchat;
USE webchat;


CREATE TABLE IF NOT EXISTS chat_users(
    id serial,
    username VARCHAR(21) NOT NULL,
    pwd VARCHAR(31) NOT NULL,
    pwd_reset_token VARCHAR(100),
    pwd_reset_expiration DATETIME,
    PRIMARY KEY (username)
);
INSERT INTO chat_users(username, pwd)
VALUES ('KumysPower', 'KumysSila123'),
    ('Jeremy34', '040204Johnson'),
    ('Danielzzz', 'easyPASSSWORD555'),
    ('AttilaJohnson', 'aJ5435345345'),
    ('FuckingCow', 'FuckingCow123');


CREATE TABLE IF NOT EXISTS chat_messages(
    msg_id INT NOT NULL,
    username VARCHAR(21) NOT NULL,
    msg VARCHAR(2000) NOT NULL,
    time_sent DATETIME NOT NULL,
    PRIMARY KEY(msg_id)
);
INSERT INTO chat_messages (username, msg, time_sent)
VALUES ('Admin', 'Hi Slaves', '9999-12-31 23:59:59');


CREATE TABLE messages_liked(
    like_id INT NOT NULL,
    msg_id int NOT NULL,
    username VARCHAR(21) NOT NULL,
    PRIMARY KEY (like_id),
    FOREIGN KEY (msg_id) REFERENCES chat_messages(msg_id),
    FOREIGN KEY (username) REFERENCES chat_users(username)
);


