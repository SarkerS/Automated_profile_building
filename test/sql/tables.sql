CREATE TABLE profiles (
    id integer PRIMARY KEY,
    platform text,
    profile_url text,
    profile_handle text,
    pic_url text,
    name text,
    bio text
);

CREATE TABLE locations (
    id integer PRIMARY KEY,
    name text,
    desc text,
    profile_id integer,
    FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);

CREATE TABLE workplaces (
    id integer PRIMARY KEY,
    name text,
    title text,
    profile_id integer,
    FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);

CREATE TABLE schools (
    id integer PRIMARY KEY,
    name text,
    desc text,
    location text,
    profile_id integer,
    FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);

CREATE TABLE tweets (
    id integer PRIMARY KEY,
    num integer,
    html text,
    profile_id integer,
    FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);
