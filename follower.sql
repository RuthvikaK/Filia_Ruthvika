CREATE TABLE follower (
    follower_id INTEGER NOT NULL,
    followed_id INTEGER NOT NULL,
    PRIMARY KEY(follower_id, followed_id),
    FOREIGN KEY(follower_id) REFERENCES filia_user(user_id) ON DELETE CASCADE,
    FOREIGN KEY(followed_id) REFERENCES filia_user(user_id) ON DELETE CASCADE
);