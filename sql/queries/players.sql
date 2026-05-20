-- name: GetPlayer :one
SELECT * FROM players
WHERE id = $1;

-- name: ListPlayers :many
SELECT * FROM players
ORDER BY name;

-- name: CreatePlayer :one
INSERT INTO players (name)
VALUES ($1)
RETURNING *;

-- name: EditPlayerName :one
UPDATE players
SET 
    name = $2,
    updated_at = NOW()
WHERE id = $1
RETURNING *;

-- name: DeletePlayer :exec
DELETE FROM players
WHERE id = $1;

-- name: GetPlayerStats :many
SELECT * FROM player_stats
WHERE player_id = $1;

-- name: GetPlayerSeasonalStats :one
SELECT * FROM player_stats
WHERE player_id = $1
AND match_type = $2
AND season = $3;

-- name: ListSeasonalStats :many
SELECT * FROM player_stats
WHERE match_type = $1
AND season = $2
ORDER BY wins;

-- name: CreatePlayerStats :one
INSERT INTO player_stats (player_id, match_type, season) 
VALUES ($1, $2, $3)
RETURNING *;

-- name: UpdatePlayerStatsWin :one
UPDATE player_stats
SET 
    wins = wins + 1,
    streak = streak + 1,
    longest_streak = $4,
    scored = $5,
    conceded = $6,
    updated_at = NOW()
WHERE player_id = $1
AND match_type = $2
AND season = $3
RETURNING *;

-- name: UpdatePlayerStatsLoss :one
UPDATE player_stats
SET 
    losses = losses + 1,
    streak = 0,
    scored = $4,
    conceded = $5,
    updated_at = NOW()
WHERE player_id = $1
AND match_type = $2
AND season = $3
RETURNING *;

-- name: UpdatePlayerStatsOtl :one
UPDATE player_stats
SET 
    otl = otl + 1,
    scored = $4,
    conceded = $5,
    updated_at = NOW()
WHERE player_id = $1
AND match_type = $2
AND season = $3
RETURNING *;
