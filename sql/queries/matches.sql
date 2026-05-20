-- name: GetMatch :one
SELECT * FROM matches
WHERE id = $1;

-- name: GetRegisteredMatches :many
SELECT * FROM matches
WHERE is_completed = TRUE;

-- name: GetDrafts :many
SELECT * FROM matches
WHERE is_completed = FALSE;

-- name: GetSeasonMatches :many
SELECT * FROM matches
WHERE is_completed = TRUE
AND match_type = $1
AND season = $2;

-- name: CreateMatch :one
INSERT INTO matches (match_type, season)
VALUES ($1, $2)
RETURNING *;

-- name: AddPlayerToMatch :one
INSERT INTO match_players (match_id, player_id, color)
VALUES ($1, $2, $3)
RETURNING *;

-- name: GetBlueTeamFromMatch :many
SELECT * FROM match_players
WHERE match_id = $1
AND color = "blue";

-- name: GetRedTeamFromMatch :many
SELECT * FROM match_players
WHERE match_id = $1
AND color = "red";

-- name: RegisterMatch :one
UPDATE matches
SET 
    blue_score = $2,
    red_score = $3,
    is_completed = TRUE,
    updated_at = NOW()
WHERE id = $1
RETURNING *;

-- name: DeleteDraft :exec
DELETE FROM matches
WHERE is_completed = FALSE
AND id = $1;
