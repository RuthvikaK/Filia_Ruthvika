CREATE TABLE photo_post (
    id SERIAL UNIQUE,
    user_id INTEGER NOT NULL,
    photo_path VARCHAR(255) NOT NULL,

    caption TEXT,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES filia_user(user_id)
);