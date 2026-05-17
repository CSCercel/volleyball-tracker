package handler

import (
	"encoding/json"
	"errors"
	"net/http"
	"strconv"

	"github.com/cscercel/volleyball-tracker/internal/service"
	"github.com/go-chi/chi/v5"
	"github.com/google/uuid"
)

type PlayerHandler struct {
	service	*service.PlayerService
}

func NewPlayerHandler(service *service.PlayerService) *PlayerHandler {
	return &PlayerHandler{service: service}
}

func (h *PlayerHandler) RegisterRoutes(r chi.Router) {
	r.Route("/players", func(r chi.Router) {
		r.Post("/", h.handleCreatePlayer)
		r.Get("/{id}/career", h.handleGetPlayerCareer)
		r.Get("/{id}/season", h.handleGetPlayerSeason)
		r.Put("/{id}", h.handleEditPlayerName)
		r.Delete("/{id}", h.handleDeletePlayer)
		r.Get("/roster", h.handleListRoster)
		r.Get("/roster/season", h.handleListSeasonRoster)
	})
}

func (h *PlayerHandler) handleGetPlayerCareer(w http.ResponseWriter, r *http.Request) {
	playerID, err := uuid.Parse(chi.URLParam(r, "id"))
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid player id", err)
		return
	}

	player, err := h.service.GetPlayerCareer(r.Context(), playerID)
	if err != nil {
		respondWithError(w, http.StatusNotFound, "player not found", err)
		return
	}

	respondWithJSON(w, http.StatusOK, player)
}

func (h *PlayerHandler) handleGetPlayerSeason(w http.ResponseWriter, r *http.Request) {
	playerID, err := uuid.Parse(chi.URLParam(r, "id"))
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid player id", err)
		return
	}
	
	// Query params
	matchType := r.URL.Query().Get("match_type")
	if matchType == "" {
		respondWithError(w, http.StatusBadRequest, "match_type is required", errors.New(""))
		return
	}

	seasonStr := r.URL.Query().Get("season")
	season, err := strconv.Atoi(seasonStr)
	if err != nil || season < 1 {
		respondWithError(w, http.StatusBadRequest, "season must be a positive number", err)
		return
	}

	player, err := h.service.GetPlayerSeason(r.Context(), playerID, matchType, season)
	if err != nil {
		respondWithError(w, http.StatusNotFound, "player not found", err)
		return
	}

	respondWithJSON(w, http.StatusOK, player)
}

func (h *PlayerHandler) handleCreatePlayer(w http.ResponseWriter, r *http.Request) {
	var body struct {
		Name 		string 	`json:"name"`
		MatchType 	string	`json:"match_type"`
		Season		int		`json:"season"`
	}

	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid request body", err)
		return
	}

	player, err := h.service.CreatePlayer(r.Context(), body.Name, body.MatchType, body.Season)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "could not create player", err)
		return
	}

	respondWithJSON(w, http.StatusCreated, player)
}

func (h *PlayerHandler) handleEditPlayerName(w http.ResponseWriter, r *http.Request) {
	playerID, err := uuid.Parse(chi.URLParam(r, "id"))
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid player id", err)
		return
	}

	var body struct {
		Name string `json:"name"`
	}

	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid request body", err)
		return
	}

	player, err := h.service.EditPlayerName(r.Context(), playerID, body.Name)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "could not change player name", err)
		return
	}

	respondWithJSON(w, http.StatusOK, player)
}

func (h *PlayerHandler) handleDeletePlayer(w http.ResponseWriter, r *http.Request) {
	playerID, err := uuid.Parse(chi.URLParam(r, "id"))
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid player id", err)
		return
	}

	if err := h.service.DeletePlayer(r.Context(), playerID); err != nil {
		respondWithError(w, http.StatusInternalServerError, "could not delete character", err)
		return
	}
	
	respondWithJSON(w, http.StatusNoContent, "")
}

func (h *PlayerHandler) handleListRoster(w http.ResponseWriter, r *http.Request) {
	roster, err := h.service.ListRoster(r.Context())
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "failed to load roster", err)
		return
	}

	respondWithJSON(w, http.StatusOK, roster)
}

func (h *PlayerHandler) handleListSeasonRoster(w http.ResponseWriter, r *http.Request) {
	// Query params
	matchType := r.URL.Query().Get("match_type")
	if matchType == "" {
		respondWithError(w, http.StatusBadRequest, "match_type is required", errors.New(""))
		return
	}

	seasonStr := r.URL.Query().Get("season")
	season, err := strconv.Atoi(seasonStr)
	if err != nil || season < 1 {
		respondWithError(w, http.StatusBadRequest, "season must be a positive number", err)
		return
	}

	roster, err := h.service.ListSeasonalRoster(r.Context(), matchType, season)
	if err != nil {
		respondWithError(w, http.StatusNotFound, "roster not found for season", err)
		return
	}

	respondWithJSON(w, http.StatusOK, roster)
}
