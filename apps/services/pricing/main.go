/*
Package main — Gateway El Salvador Real-Time Pricing Service

Dynamic pricing engine for:
  - Short-term rental rate optimization
  - Tour demand-based pricing
  - BTC/USD real-time conversion
  - Seasonal and event-based price adjustments
*/
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/cors"
)

func main() {
	port := os.Getenv("PRICING_SERVICE_PORT")
	if port == "" {
		port = "8003"
	}

	r := chi.NewRouter()

	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(cors.Handler(cors.Options{
		AllowedOrigins: []string{"http://localhost:3000", "http://localhost:8000"},
		AllowedMethods: []string{"GET", "POST", "OPTIONS"},
		AllowedHeaders: []string{"Accept", "Authorization", "Content-Type"},
	}))

	r.Get("/health", func(w http.ResponseWriter, r *http.Request) {
		respondJSON(w, http.StatusOK, map[string]string{
			"status":  "healthy",
			"service": "pricing",
		})
	})

	r.Route("/api/pricing", func(r chi.Router) {
		r.Get("/rental/{propertyId}", getRentalPricingHandler)
		r.Get("/tour/{tourId}", getTourPricingHandler)
		r.Get("/btc/rate", getBtcRateHandler)
	})

	log.Printf("🇸🇻 Pricing service starting on port %s", port)
	if err := http.ListenAndServe(fmt.Sprintf(":%s", port), r); err != nil {
		log.Fatal(err)
	}
}

func getRentalPricingHandler(w http.ResponseWriter, r *http.Request) {
	propertyID := chi.URLParam(r, "propertyId")
	// TODO: Dynamic pricing based on demand, season, events
	respondJSON(w, http.StatusOK, map[string]interface{}{
		"property_id":    propertyID,
		"nightly_rate":   0,
		"currency":       "USD",
		"pricing_model":  "base",
	})
}

func getTourPricingHandler(w http.ResponseWriter, r *http.Request) {
	tourID := chi.URLParam(r, "tourId")
	respondJSON(w, http.StatusOK, map[string]interface{}{
		"tour_id":  tourID,
		"price":    0,
		"currency": "USD",
	})
}

func getBtcRateHandler(w http.ResponseWriter, r *http.Request) {
	// TODO: Fetch real-time BTC/USD rate, cache in Redis
	respondJSON(w, http.StatusOK, map[string]interface{}{
		"btc_usd":    0,
		"sats_per_dollar": 0,
		"source":     "coingecko",
		"cached":     false,
	})
}

func respondJSON(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(data)
}
