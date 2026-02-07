# ── Go Microservice (Multi-stage Build) ──
FROM golang:1.22-alpine AS builder

WORKDIR /app
COPY go.mod go.sum* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /service .

FROM alpine:3.20
RUN apk --no-cache add ca-certificates
COPY --from=builder /service /service
EXPOSE 8001 8002 8003
CMD ["/service"]
