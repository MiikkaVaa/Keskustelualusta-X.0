CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    is_admin BOOLEAN DEFAULT FALSE
);

CREATE TABLE forums (
    id SERIAL PRIMARY KEY,
    name TEXT,
    user_id INTEGER REFERENCES users(id),
    private BOOLEAN DEFAULT FALSE
);
