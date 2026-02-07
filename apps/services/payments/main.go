/*
Package main — Gateway El Salvador Payments Service

High-concurrency payment processing microservice handling:
  - Stripe checkout sessions (fiat: card, ACH)
  - Bitcoin Lightning payments (aligned with ES legal tender law)
  - Webhook processing for payment confirmations
  - Foundation revenue allocation (10-20% of gross)
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
	port := os.Getenv("PAYMENTS_SERVICE_PORT")
	if port == "" {
		port = "8001"
	}

	r := chi.NewRouter()

	// Middleware
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(middleware.RequestID)
	r.Use(cors.Handler(cors.Options{
		AllowedOrigins:   []string{"http://localhost:3000", "http://localhost:8000"},
		AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"Accept", "Authorization", "Content-Type"},
		AllowCredentials: true,
	}))

	// Routes
	r.Get("/health", healthHandler)
	r.Route("/api/payments", func(r chi.Router) {
		r.Post("/checkout", createCheckoutHandler)
		r.Post("/webhook/stripe", stripeWebhookHandler)
		r.Post("/lightning/invoice", createLightningInvoiceHandler)
		r.Get("/lightning/invoice/{invoiceId}", checkLightningPaymentHandler)
	})

	log.Printf("🇸🇻 Payments service starting on port %s", port)
	if err := http.ListenAndServe(fmt.Sprintf(":%s", port), r); err != nil {
		log.Fatal(err)
	}
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	respondJSON(w, http.StatusOK, map[string]string{
		"status":  "healthy",
		"service": "payments",
	})
}

func createCheckoutHandler(w http.ResponseWriter, r *http.Request) {
	// TODO: Create Stripe checkout session
	// TODO: Calculate Foundation allocation
	respondJSON(w, http.StatusOK, map[string]string{
		"status": "checkout_created",
	})
}

func stripeWebhookHandler(w http.ResponseWriter, r *http.Request) {
	// TODO: Verify Stripe webhook signature
	// TODO: Process payment confirmation
	// TODO: Allocate Foundation percentage
	// TODO: Record impact transaction
	respondJSON(w, http.StatusOK, map[string]string{
		"status": "webhook_received",
	})
}

func createLightningInvoiceHandler(w http.ResponseWriter, r *http.Request) {
	// TODO: Create Lightning Network invoice via LND
	respondJSON(w, http.StatusOK, map[string]string{
		"status": "lightning_invoice_created",
	})
}

func checkLightningPaymentHandler(w http.ResponseWriter, r *http.Request) {
	invoiceID := chi.URLParam(r, "invoiceId")
	// TODO: Check Lightning payment status
	respondJSON(w, http.StatusOK, map[string]interface{}{
		"invoice_id": invoiceID,
		"status":     "pending",
	})
}

func respondJSON(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(data)
}
