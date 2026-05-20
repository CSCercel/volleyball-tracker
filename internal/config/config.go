package config

import (
	"fmt"
	"os"
	"strconv"

	"github.com/joho/godotenv"
)

type Config struct {
	DatabaseURL			string
	Port				string
	JWTSecret			string
	JWTExpiryHours		int
	RegistrationCode	string
	FrontendURL			string
}

func Load() (*Config, error) {
	godotenv.Load()

	expiryHours := 24
	if v := os.Getenv("JWT_EXPIRY_HOURS"); v != "" {
		if n, err := strconv.Atoi(v); err == nil {
			expiryHours = n
		}
	}

	cfg := &Config{
		DatabaseURL: os.Getenv("DATABASE_URL"),
		Port: os.Getenv("PORT"),
		JWTSecret: os.Getenv("JWT_SECRET"),
		JWTExpiryHours: expiryHours,
		RegistrationCode: os.Getenv("REGISTRATION_CODE"),
		FrontendURL: os.Getenv("FRONTEND_URL"),
	}

	if cfg.DatabaseURL == "" {
		return nil, fmt.Errorf("DATABASE_URL is required")
	}
	if cfg.Port == "" {
		return nil, fmt.Errorf("PORT is required")
	}
	if cfg.JWTSecret == "" {
		return nil, fmt.Errorf("JWT_SECRET is required")
	}
	if cfg.RegistrationCode == "" {
		return nil, fmt.Errorf("REGISTRATION_CODE is required")
	}
	if cfg.FrontendURL == "" {
		return nil, fmt.Errorf("FrontendURL is required")
	}

	return cfg, nil
}
