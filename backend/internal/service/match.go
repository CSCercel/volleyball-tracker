package service

import (
	"context"
	"fmt"

	"github.com/cscercel/volleyball-tracker/internal/db"
	"github.com/google/uuid"
)

type MatchService struct {
	queries	*db.Queries
}

func NewMatchService(queries *db.Queries) *MatchService {
	return &MatchService{queries: queries}
}

func (s *MatchService) GetMatch(ctx context.Context, match_id uuid.UUID) (db.Match, error) {
	match, err := s.queries.GetMatch(ctx, match_id)
	if err != nil {
		return db.Match{}, fmt.Errorf("unable to get match: %w", err)
	}

	return match, nil
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
