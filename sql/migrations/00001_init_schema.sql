-- +goose Up
CREATE TABLE users (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    email           TEXT        NOT NULL UNIQUE,
    hashed_password TEXT        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE players (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT        NOT NULL UNIQUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE player_stats (
    id              UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id       UUID    NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    match_type      TEXT    NOT NULL CHECK (match_type IN ('indoor', 'beach')),
    season          INTEGER NOT NULL,
    wins            INTEGER NOT NULL DEFAULT 0,
    losses          INTEGER NOT NULL DEFAULT 0,
    otl             INTEGER NOT NULL DEFAULT 0,
    streak          INTEGER NOT NULL DEFAULT 0,
    longest_streak  INTEGER NOT NULL DEFAULT 0,
    scored          INTEGER NOT NULL DEFAULT 0,
    conceded        INTEGER NOT NULL DEFAULT 0,
    UNIQUE(player_id, match_type, season)
);

CREATE TABLE matches (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    match_type      TEXT        NOT NULL CHECK (match_type IN ('indoor', 'beach')),
    season          INTEGER     NOT NULL,
    blue_score      INTEGER     NOT NULL DEFAULT 0,
    red_score       INTEGER     NOT NULL DEFAULT 0,
    is_completed    BOOLEAN     DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE match_players (
    id          UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id    UUID    NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    player_id   UUID    NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    color       TEXT    NOT NULL CHECK (color IN ('blue', 'red'))
);

-- +goose Down
DROP TABLE users;
DROP TABLE players;
DROP TABLE player_stats;
DROP TABLE matches;
DROP TABLE match_players;
