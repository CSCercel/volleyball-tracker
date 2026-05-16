package handler

import (
	"net/http"
)

func HandleHealth(w http.ResponseWriter, r *http.Request) {
	respondWithJSON(w, http.StatusOK, map[string]string{"status": "healthy"})
}
