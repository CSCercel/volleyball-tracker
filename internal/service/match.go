package service

import (
	"context"
	"fmt"
	"math"
	"time"

	"github.com/cscercel/volleyball-tracker/internal/db"
	"github.com/google/uuid"
)

type MatchService struct {
	queries	*db.Queries
}

type MatchWithPlayers struct {
	Match		db.Match			`json:"match"`
	BlueTeam	[]db.MatchPlayer	`json:"blue_team"`
	RedTeam		[]db.MatchPlayer	`json:"red_team"`
}

type TeamPerformance struct {
	Players		[]db.MatchPlayer	`json:"players"`
	Scored		int					`json:"scored"`
	Conceded	int					`json:"conceded"`
	IsWinner	bool				`json:"is_winner"`
	IsOtl		bool				`json:"is_otl"`
}

func NewMatchService(queries *db.Queries) *MatchService {
	return &MatchService{queries: queries}
}

func (s *MatchService) GetMatch(ctx context.Context, match_id uuid.UUID) (MatchWithPlayers, error) {
	match, err := s.queries.GetMatch(ctx, match_id)
	if err != nil {
		return MatchWithPlayers{}, fmt.Errorf("unable to get match: %w", err)
	}

	blue_team, err := s.queries.GetBlueTeamFromMatch(ctx, match.ID)
	if err != nil {
		return MatchWithPlayers{}, fmt.Errorf("failed to load blue team: %w", err)
	}

	red_team, err := s.queries.GetRedTeamFromMatch(ctx, match.ID)
	if err != nil {
		return MatchWithPlayers{}, fmt.Errorf("failed to load red team: %w", err)
	}

	return MatchWithPlayers{
		Match: match,
		BlueTeam: blue_team,
		RedTeam: red_team,
	}, nil
}

func (s *MatchService) GetRegisteredMatches(ctx context.Context) ([]db.Match, error) {
	matches, err := s.queries.GetRegisteredMatches(ctx)
	if err != nil {
		return []db.Match{}, fmt.Errorf("unable to get registered matches: %w", err)
	}

	return matches, nil
}

func (s *MatchService) GetDrafts(ctx context.Context) ([]db.Match, error) {
	drafts, err := s.queries.GetDrafts(ctx)
	if err != nil {
		return []db.Match{}, fmt.Errorf("unable to get drafts: %w", err)
	}

	return drafts, nil
}

func (s *MatchService) GetSeasonMatches(ctx context.Context, match_type string, season int) ([]db.Match, error) {
	params := db.GetSeasonMatchesParams{
		MatchType: match_type,
		Season: int32(season),
	}

	matches, err := s.queries.GetSeasonMatches(ctx, params)
	if err != nil {
		return []db.Match{}, fmt.Errorf("unable to get seasonal matches: %w", err)
	}

	return matches, nil
}

func (s *MatchService) CreateMatch(
	ctx context.Context, match_type string, blue_players, red_players []db.Player,
) (MatchWithPlayers, error) {
	if match_type != "indoor" && match_type != "beach" {
		return MatchWithPlayers{}, fmt.Errorf("invalid match_type: expected `indoor` or `beach`, got %s", match_type)
	}

	season := time.Now().UTC().Year()

	params := db.CreateMatchParams{
		MatchType: match_type,
		Season: int32(season),
	}

	match, err := s.queries.CreateMatch(ctx, params)
	if err != nil {
		return MatchWithPlayers{}, fmt.Errorf("could not create match: %w", err)
	}

	// Add players from blue_team
	blue_team := []db.MatchPlayer{}
	for _, player := range blue_players {
		player, err := s.queries.AddPlayerToMatch(ctx, db.AddPlayerToMatchParams{
			MatchID: match.ID,
			PlayerID: player.ID,
			Color: "blue",
		})
		if err != nil {
			return MatchWithPlayers{}, fmt.Errorf("failed to add players from blue_team: %w", err)
		}

		blue_team = append(blue_team, player)
	}

	// idem. for red_team
	red_team := []db.MatchPlayer{}
	for _, player := range red_players {
		player, err := s.queries.AddPlayerToMatch(ctx, db.AddPlayerToMatchParams{
			MatchID: match.ID,
			PlayerID: player.ID,
			Color: "red",
		})
		if err != nil {
			return MatchWithPlayers{}, fmt.Errorf("failed to add players from red_team: %w", err)
		}

		red_team = append(red_team, player)
	}

	return MatchWithPlayers{
		Match: match,
		BlueTeam: blue_team,
		RedTeam: red_team,
	}, nil
}

func (s *MatchService) RegisterMatch(
	ctx context.Context, match_id uuid.UUID, blue_score, red_score int,
) (db.Match, error) {
	// Check scores
	if blue_score == red_score {
		return db.Match{}, fmt.Errorf("cannot determine winner")
	}

	is_overtime := false
	if math.Abs(float64(blue_score) - float64(red_score)) == 2 {
		is_overtime = true
	}

	// Get Match
	params := db.RegisterMatchParams{
		ID: match_id,
		BlueScore: int32(blue_score),
		RedScore: int32(red_score),
	}
	match, err := s.queries.RegisterMatch(ctx, params)	
	if err != nil {
		return db.Match{}, fmt.Errorf("failed to get match for registration: %w", err)
	}

	// Get Blue Team & Red Team
	blue_team, err := s.queries.GetBlueTeamFromMatch(ctx, match.ID)
	if err != nil {
		return db.Match{}, fmt.Errorf("failed to load blue team from match: %w", err)
	}

	red_team, err := s.queries.GetRedTeamFromMatch(ctx, match.ID)
	if err != nil {
		return db.Match{}, fmt.Errorf("failed to load red team from match: %w", err)
	}

	// Match results
	blue_performance := TeamPerformance{
		Players: blue_team,
		Scored: blue_score,
		Conceded: red_score,
		IsWinner: (blue_score > red_score),
		IsOtl: (blue_score < red_score) && is_overtime,
	}

	for _, player := range blue_performance.Players {
		if blue_performance.IsWinner {
			_, err := s.queries.UpdatePlayerStatsWin(ctx, db.UpdatePlayerStatsWinParams{
					PlayerID: player.ID,
					MatchType: match.MatchType,
					Season: int32(match.Season),
					Scored: int32(blue_performance.Scored),
					Conceded: int32(blue_performance.Conceded),
			})
			if err != nil {
				return db.Match{}, fmt.Errorf("failed to declare blue as winner: %w", err)
			}
		} else if blue_performance.IsOtl {
			_, err := s.queries.UpdatePlayerStatsOtl(ctx, db.UpdatePlayerStatsOtlParams{
				PlayerID: player.ID,
				MatchType: match.MatchType,
				Season: int32(match.Season),
				Scored: int32(blue_performance.Scored),
				Conceded: int32(blue_performance.Conceded),
			})
			if err != nil {
				return db.Match{}, fmt.Errorf("failed to declare blue as overtime loser: %w", err)
			}
		} else {
			_, err := s.queries.UpdatePlayerStatsLoss(ctx, db.UpdatePlayerStatsLossParams{
				PlayerID: player.ID,
				MatchType: match.MatchType,
				Season: int32(match.Season),
				Scored: int32(blue_performance.Scored),
				Conceded: int32(blue_performance.Conceded),
			})
			if err != nil {
				return db.Match{}, fmt.Errorf("failed to declare blue as overtime loser: %w", err)
			}
		}
	}

	red_performance := TeamPerformance{
		Players: red_team,
		Scored: red_score,
		Conceded: blue_score,
	}
}
