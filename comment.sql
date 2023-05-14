CREATE TABLE comment (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    user_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES filia_user(user_id) ON DELETE CASCADE
);