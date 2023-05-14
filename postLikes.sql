CREATE TABLE post_likes (
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    PRIMARY KEY(user_id, post_id),
    FOREIGN KEY(user_id) REFERENCES filia_user(user_id) ON DELETE CASCADE,
    FOREIGN KEY(post_id) REFERENCES photo_post(id) ON DELETE CASCADE
);