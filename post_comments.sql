CREATE TABLE post_comments (
    post_id INTEGER NOT NULL,
    comment_id INTEGER NOT NULL,
    PRIMARY KEY(post_id, comment_id),
    FOREIGN KEY(post_id) REFERENCES photo_post(id) ON DELETE CASCADE,
    FOREIGN KEY(comment_id) REFERENCES comment(id) ON DELETE CASCADE
);