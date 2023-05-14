-- create a table with user's info that we collect

CREATE TABLE filia_user (
    user_id SERIAL UNIQUE,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    email  VARCHAR(255) UNIQUE NOT NULL UNIQUE,
    phone  VARCHAR(16) UNIQUE NOT NULL UNIQUE,
    gender  VARCHAR(255),
    major  VARCHAR(255) NOT NULL,
    profile_path VARCHAR(255) NOT NULL,
    grad_date VARCHAR(255) NOT NULL,
    bio VARCHAR(255) NOT NULL,
    profile_path VARCHAR(255) NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY (user_id)
);