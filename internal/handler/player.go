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


// @Summary      Get Player Career
// @Tags         players
// @Produce      json
// @Param        id   path      string  true  "Player ID"
// @Success      200  {array}   service.PlayerWithStats
// @Failure      400  {object}  object{error=string}
// @Failure      404  {object}  object{error=string}
// @Router       /api/v1/players/{id}/career [get]
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

// @Summary      Get Player Season
// @Tags         players
// @Produce      json
// @Param        id   		path  		string  true  "Player ID"
// @Param        match_type query  		string  true  "Match Type"
// @Param        season   	query      	integer true  "Season"
// @Success      200  		{array}   	service.PlayerWithStats
// @Failure      400  		{object}  	object{error=string}
// @Failure      404  		{object}  	object{error=string}
// @Router       /api/v1/players/{id}/season [get]
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

// @Summary      Create Player
// @Tags         players
// @Produce      json
// @Param        body body      object{name=string} true "Player Body"
// @Success      201  {array}   service.PlayerWithStats
// @Failure      400  {object}  object{error=string}
// @Failure      500  {object}  object{error=string}
// @Router       /api/v1/players [post]
func (h *PlayerHandler) handleCreatePlayer(w http.ResponseWriter, r *http.Request) {
	var body struct {
		Name 		string 	`json:"name"`
	}

	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid request body", err)
		return
	}

	player, err := h.service.CreatePlayer(r.Context(), body.Name)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "could not create player", err)
		return
	}

	respondWithJSON(w, http.StatusCreated, player)
}

// @Summary      Edit Player Name
// @Description  Updates the name of an existing player by their UUID
// @Tags         players
// @Accept       json
// @Produce      json
// @Param        id   path      string                true  "Player UUID" format(uuid)
// @Param        body body      object{name=string}   true  "New Player Name"
// @Success      200  {object}  service.PlayerWithStats
// @Failure      400  {object}  object{error=string}
// @Failure      500  {object}  object{error=string}
// @Router       /api/v1/players/{id}/name [put]
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

// @Summary      Delete Player
// @Tags         players
// @Produce      json
// @Param        id   path      string                true  "Player UUID" format(uuid)
// @Success      204  
// @Failure      400  {object}  object{error=string}
// @Failure      500  {object}  object{error=string}
// @Router       /api/v1/players/{id} [delete]
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

// @Summary      List Roster
// @Tags         players
// @Produce      json
// @Success      200  {array}   object{id=string, name=string}
// @Failure      500  {object}  object{error=string}
// @Router       /api/v1/players/roster [get]
func (h *PlayerHandler) handleListRoster(w http.ResponseWriter, r *http.Request) {
	roster, err := h.service.ListRoster(r.Context())
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "failed to load roster", err)
		return
	}

	respondWithJSON(w, http.StatusOK, roster)
}

// @Summary      List Seasonal Roster
// @Tags         players
// @Produce      json
// @Param        match_type query  		string  true  "Match Type"
// @Param        season   	query      	integer true  "Season"
// @Success      200  		{array}   	service.PlayerWithStats
// @Failure      400  		{object}  	object{error=string}
// @Failure      404  		{object}  	object{error=string}
// @Router       /api/v1/players/roster/season [get]
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
