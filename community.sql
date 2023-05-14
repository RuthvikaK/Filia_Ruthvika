-- Aaloki --
CREATE TABLE community (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    creator_id INTEGER REFERENCES filia_user(user_id)
);