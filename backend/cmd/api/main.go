package main

import (
	"context"
	"log"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	// "github.com/go-chi/cors"
	_ "github.com/lib/pq"

	"github.com/cscercel/volleyball-tracker/internal/config"
	"github.com/cscercel/volleyball-tracker/internal/db"
	"github.com/cscercel/volleyball-tracker/internal/handler"
	"github.com/cscercel/volleyball-tracker/internal/repository"
	"github.com/cscercel/volleyball-tracker/internal/service"
)

func main() {

	// Load Config
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("failed to load config: %v", err)
	}

	ctx := context.Background()

	// Connect to Database
	pool, err := repository.NewPool(ctx, cfg.DatabaseURL)
	if err != nil {
		log.Fatalf("failed to connect to database: %v", err)
	}
	defer pool.Close()

	// Instantiate API
	queries := db.New(pool)
	playerService := service.NewPlayerService(queries)
	playerHandler := handler.NewPlayerHandler(playerService)

	// Routers
	r := chi.NewRouter()

	// r.Use(cors.Handler(cors.Options{
	// 	AllowedOrigins:   []string{"https://*", "http://*"},
	// 	AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
	// 	AllowedHeaders:   []string{"*"},
	// 	ExposedHeaders:   []string{"Link"},
	// 	AllowCredentials: false,
	// 	MaxAge:           300,
	// }))

	// Global middleware
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)

	// Routes
	r.Route("/api/v1", func(r chi.Router) {
		playerHandler.RegisterRoutes(r)
	})

	r.Get("/healthz", handler.HandleHealth)

	// Start server
	srv := &http.Server{
		Addr: ":" + cfg.Port,
		Handler: r,
	}

	log.Printf("server running on port: %v", cfg.Port)
	if err := srv.ListenAndServe(); err != nil {
		log.Fatalf("server error: %v", err)
	}
}
