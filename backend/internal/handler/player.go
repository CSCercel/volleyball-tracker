package handler

import (
	"encoding/json"
	"net/http"
	"strconv"

	"github.com/cscercel/volleyball-tracker/internal/service"
	"github.com/go-chi/chi/v5"
	"github.com/google/uuid"
)

type PlayerHandler struct {
	playerService	*service.PlayerService
}

func (h *PlayerHandler) GetPlayerCareer(w http.ResponseWriter, r *http.Request) {
	playerID, err := uuid.Parse(chi.URLParam(r, "id"))
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid player id", err)
		return
	}

	player, err := h.playerService.GetPlayerCareer(r.Context(), playerID)
	if err != nil {
		respondWithError(w, http.StatusNotFound, "player not found", err)
		return
	}

	respondWithJSON(w, http.StatusOK, player)
}

func (h *PlayerHandler) GetPlayerSeason(w http.ResponseWriter, r *http.Request) {
	playerID, err := uuid.Parse(chi.URLParam(r, "id"))
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid player id", err)
		return
	}
	
	// Query params
	matchType := r.URL.Query().Get("match_type")
	if matchType == "" {
		respondWithError(w, http.StatusBadRequest, "match_type is required", err)
		return
	}

	seasonStr := r.URL.Query().Get("season")
	season, err := strconv.Atoi(seasonStr)
	if err != nil || season < 1 {
		respondWithError(w, http.StatusBadRequest, "season must be a positive number", err)
		return
	}

	player, err := h.playerService.GetPlayerSeason(r.Context(), playerID, matchType, season)
	if err != nil {
		respondWithError(w, http.StatusNotFound, "player not found", err)
		return
	}

	respondWithJSON(w, http.StatusOK, player)
}

func (h *PlayerHandler) CreatePlayer(w http.ResponseWriter, r *http.Request) {
	var body struct {
		Name 		string 	`json:"name"`
		MatchType 	string	`json:"match_type"`
		Season		int		`json:"season"`
	}

	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid request body", err)
		return
	}

	player, err := 
}
