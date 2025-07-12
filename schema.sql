CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    location TEXT,
    availability TEXT,
    is_public INTEGER DEFAULT 1,
    is_admin INTEGER DEFAULT 0,
    is_banned INTEGER DEFAULT 0
);

CREATE TABLE skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
buster
    skill TEXT NOT NULL,
    type TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE swaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requester_id INTEGER,
    requester_skill_id INTEGER,
    receiver_id INTEGER,
    receiver_skill_id INTEGER,
    status TEXT NOT NULL,
    rating INTEGER,
    comment TEXT,
    FOREIGN KEY (requester_id) REFERENCES users(id),
    FOREIGN KEY (requester_skill_id) REFERENCES skills(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id),
    FOREIGN KEY (receiver_skill_id) REFERENCES skills(id)
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL,
    created_at DATETIME NOT NULL
);