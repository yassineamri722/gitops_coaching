# Stage 1: Builder
FROM python:3.11-slim as builder
WORKDIR /app
COPY . .

# Stage 2: Runtime minimale
FROM python:3.11-alpine
WORKDIR /app
COPY --from=builder /app .

EXPOSE 3000

CMD ["python", "-m", "http.server", "3000", "--directory", "."]
