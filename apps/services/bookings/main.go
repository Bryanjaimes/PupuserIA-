/*
Package main — Gateway El Salvador Bookings Service

Booking orchestration microservice handling:
  - Tour & experience booking lifecycle
  - Short-term rental reservations
  - Consulting session scheduling
  - Guest communication automation
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
	port := os.Getenv("BOOKINGS_SERVICE_PORT")
	if port == "" {
		port = "8002"
	}

	r := chi.NewRouter()

	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(middleware.RequestID)
	r.Use(cors.Handler(cors.Options{
		AllowedOrigins: []string{"http://localhost:3000", "http://localhost:8000"},
		AllowedMethods: []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders: []string{"Accept", "Authorization", "Content-Type"},
	}))

	r.Get("/health", func(w http.ResponseWriter, r *http.Request) {
		respondJSON(w, http.StatusOK, map[string]string{
			"status":  "healthy",
			"service": "bookings",
		})
	})

	r.Route("/api/bookings", func(r chi.Router) {
		// Tour bookings
		r.Post("/tours", createTourBookingHandler)
		r.Get("/tours/{bookingId}", getTourBookingHandler)
		r.Put("/tours/{bookingId}/cancel", cancelTourBookingHandler)

		// Rental bookings
		r.Post("/rentals", createRentalBookingHandler)
		r.Get("/rentals/{bookingId}", getRentalBookingHandler)

		// Consulting sessions
		r.Post("/consulting", createConsultingBookingHandler)
	})

	log.Printf("🇸🇻 Bookings service starting on port %s", port)
	if err := http.ListenAndServe(fmt.Sprintf(":%s", port), r); err != nil {
		log.Fatal(err)
	}
}

func createTourBookingHandler(w http.ResponseWriter, r *http.Request) {
	// TODO: Validate availability, create booking, trigger payment
	respondJSON(w, http.StatusCreated, map[string]string{"status": "tour_booking_created"})
}

func getTourBookingHandler(w http.ResponseWriter, r *http.Request) {
	bookingID := chi.URLParam(r, "bookingId")
	respondJSON(w, http.StatusOK, map[string]string{"booking_id": bookingID, "status": "confirmed"})
}

func cancelTourBookingHandler(w http.ResponseWriter, r *http.Request) {
	bookingID := chi.URLParam(r, "bookingId")
	respondJSON(w, http.StatusOK, map[string]string{"booking_id": bookingID, "status": "cancelled"})
}

func createRentalBookingHandler(w http.ResponseWriter, r *http.Request) {
	respondJSON(w, http.StatusCreated, map[string]string{"status": "rental_booking_created"})
}

func getRentalBookingHandler(w http.ResponseWriter, r *http.Request) {
	bookingID := chi.URLParam(r, "bookingId")
	respondJSON(w, http.StatusOK, map[string]string{"booking_id": bookingID, "status": "confirmed"})
}

func createConsultingBookingHandler(w http.ResponseWriter, r *http.Request) {
	respondJSON(w, http.StatusCreated, map[string]string{"status": "consulting_booked"})
}

func respondJSON(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(data)
}
