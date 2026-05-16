package service

import (
	"context"
	"fmt"

	"github.com/cscercel/volleyball-tracker/internal/db"
	"github.com/google/uuid"
)

type PlayerService struct {
	queries	*db.Queries
}

type PlayerStats struct {
	Stats			db.PlayerStat	`json:"stats"`
	Played			int32			`json:"played"`
	WinLossRatio	float64			`json:"winloss_ratio"`
	EfficiencyRatio	float64			`json:"efficiency_ratio"`
	Points			int32			`json:"points"`
}

type PlayerWithStats struct {
	PlayerName	string			`json:"player_name"`
	PlayerStats	[]PlayerStats	`json:"player_stats"`
}

func NewPlayerService(queries *db.Queries) *PlayerService {
	return &PlayerService{queries: queries}
}

func ComputePlayerStats(stats db.PlayerStat) PlayerStats {
	// Calculate matches played and points
	played := stats.Wins + stats.Losses + stats.Otl
	points := 2 * stats.Wins + stats.Otl

	// Calculate ratios
	winloss_ratio := 0.0
	efficiency_ratio := 0.0

	if played > 0 {
		winloss_ratio = float64(stats.Wins) / float64(played)
	}

	if stats.Conceded > 0 {
		efficiency_ratio = float64(stats.Scored) / float64(stats.Conceded)
	}

	return PlayerStats{
		Stats: stats,
		Played: int32(played),
		Points: int32(points),
		WinLossRatio: winloss_ratio,
		EfficiencyRatio: efficiency_ratio,
	}
}

func (s *PlayerService) GetPlayerCareer(ctx context.Context, playerID uuid.UUID) (PlayerWithStats, error) {
	player, err := s.queries.GetPlayer(ctx, playerID)
	if err != nil {
		return PlayerWithStats{}, fmt.Errorf("unable to get player: %w", err)
	}
	
	// Get Stats
	stats, err := s.queries.GetPlayerStats(ctx, playerID)
	if err != nil {
		return PlayerWithStats{}, fmt.Errorf("could not load player stats: %w", err)
	}

	player_stats := []PlayerStats{}
	for _, stat := range stats {
		player_stats = append(player_stats, ComputePlayerStats(stat))
	}

	return PlayerWithStats{
		PlayerName: player.Name,
		PlayerStats: player_stats,
	}, nil
}

func (s *PlayerService) GetPlayerSeason(
	ctx context.Context, playerID uuid.UUID, match_type string, season int,
) (PlayerWithStats, error) {
	player, err := s.queries.GetPlayer(ctx, playerID)
	if err != nil {
		return PlayerWithStats{}, fmt.Errorf("no player found: %w", err)
	}
	
	// Get Stats
	params := db.GetPlayerSeasonalStatsParams{
		PlayerID: playerID,
		MatchType: match_type,
		Season: int32(season),
	}

	stats, err := s.queries.GetPlayerSeasonalStats(ctx, params)
	if err != nil {
		return PlayerWithStats{}, fmt.Errorf("could not load player stats: %w", err)
	}

	player_stats := []PlayerStats{ComputePlayerStats(stats)}

	return PlayerWithStats{
		PlayerName: player.Name,
		PlayerStats: player_stats,
	}, nil
}

func (s *PlayerService) CreatePlayer(
	ctx context.Context, playerName, match_type string, season int,
) (PlayerWithStats, error) {
	player, err := s.queries.CreatePlayer(ctx, playerName)
	if err != nil {
		return PlayerWithStats{}, fmt.Errorf("could not create player: %w", err)		
	}

	// Initialize stats (TODO remove initialization of stats will handle this in match registration)
	params := db.CreatePlayerStatsParams{
		PlayerID: player.ID,
		MatchType: match_type,
		Season: int32(season),
	}

	stats, err := s.queries.CreatePlayerStats(ctx, params)
	if err != nil {
		return PlayerWithStats{}, fmt.Errorf("could not initialize player stats: %w", err)
	}

	player_stats := []PlayerStats{ComputePlayerStats(stats)}

	return PlayerWithStats{
		PlayerName: player.Name,
		PlayerStats: player_stats,
	}, nil
}

func (s *PlayerService) EditPlayerName(ctx context.Context, playerID uuid.UUID, name string) (db.Player, error) {
	params := db.EditPlayerNameParams{
		ID: playerID,
		Name: name,
	}

	player, err := s.queries.EditPlayerName(ctx, params)
	if err != nil {
		return db.Player{}, fmt.Errorf("could not change player name: %w", err)
	}

	return player, nil
}

func (s *PlayerService) DeletePlayer(ctx context.Context, playerID uuid.UUID) error {
	if err := s.queries.DeletePlayer(ctx, playerID); err != nil {
		return fmt.Errorf("could not delete player: %w", err)
	}
	
	return nil
}

func (s *PlayerService) ListRoster(ctx context.Context) ([]db.Player, error) {
	roster, err := s.queries.ListPlayers(ctx)
	if err != nil {
		return []db.Player{}, fmt.Errorf("could not list roster: %w", err)
	}

	// No need to fetch stats for entire roster, will be ONLY season specific
	// We just want the names here for a dropdown list on the client side
	return roster, nil
}

func (s *PlayerService) ListSeasonalRoster(
	ctx context.Context, match_type string, season int,
) ([]PlayerWithStats, error) {
	roster, err := s.queries.ListPlayers(ctx)
	if err != nil {
		return []PlayerWithStats{}, fmt.Errorf("could not list roster: %w", err)
	}

	params := db.ListSeasonalStatsParams{
		MatchType: match_type,
		Season: int32(season),
	}
	
	// Merge stats
	stats, err := s.queries.ListSeasonalStats(ctx, params)
	if err != nil {
		return []PlayerWithStats{}, fmt.Errorf("could not load seasonal stats: %w", err)
	}

	// Create a map to lookup name
	nameMap := make(map[uuid.UUID]string)
	for _, p := range roster {
		nameMap[p.ID] = p.Name
	}

	players := []PlayerWithStats{}

	for i := range stats {
		id := stats[i].PlayerID
		if name, ok := nameMap[id]; ok {
			player_stats := []PlayerStats{ComputePlayerStats(stats[i])}
			player := PlayerWithStats{PlayerName: name, PlayerStats: player_stats}	
			players = append(players, player)
		}
	}

	return players, nil
}
