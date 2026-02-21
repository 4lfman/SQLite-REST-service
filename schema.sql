PRAGMA foreign_keys=OFF;

DROP TABLE IF EXISTS theatres;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS screenings;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS customers;

PRAGMA foreign_keys=ON;

CREATE TABLE theatres (
    t_name      TEXT,
    capacity    INT,
    PRIMARY KEY (t_name)
);

CREATE TABLE movies (
    imdb        TEXT,
    title       TEXT,
    year        INT,
    duration    INT,
    PRIMARY KEY (imdb)
);

CREATE TABLE screenings (
    s_id        TEXT DEFAULT (lower(hex(randomblob(32)))),
    imdb        TEXT,
    t_name      TEXT,
    date        DATE,
    time        TIME,
    PRIMARY KEY (s_id),
    UNIQUE (imdb, t_name, date, time),
    FOREIGN KEY (imdb) REFERENCES movies(imdb),
    FOREIGN KEY (t_name) REFERENCES theatres(t_name)
);

CREATE TABLE tickets (
    id          TEXT DEFAULT (lower(hex(randomblob(16)))),
    u_name      TEXT,
    s_id        TEXT,
    PRIMARY KEY (id),
    FOREIGN KEY (u_name) REFERENCES customers(u_name),
    FOREIGN KEY (s_id) REFERENCES screenings(s_id)
);

CREATE TABLE customers (
    u_name      TEXT,
    full_name   TEXT,
    pwd         TEXT,
    PRIMARY KEY (u_name)
);

INSERT INTO theatres(t_name, capacity) VALUES
    ('Kino', 10),
    ('Regal', 16),
    ('Skandia', 100);