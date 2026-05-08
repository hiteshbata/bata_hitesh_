# Krushi AI Assistant

A WhatsApp-based AI assistant for Indian farmers, providing crop health insights using satellite, weather data, and AI.

## Project Structure

This is a monorepo containing:

- `apps/api`: Python FastAPI backend orchestrating AI workflows, geospatial data, and WhatsApp webhooks. Uses Celery and Redis for async task processing.
- `apps/web`: Next.js 14 frontend admin dashboard.
- `database`: SQL migration scripts for Supabase (PostgreSQL).

## Prerequisites

- Docker and docker-compose
- Node.js (v20+)
- Python (v3.11+)

## Local Development (Docker)

1. Copy `.env.example` to `.env` in `apps/api` and `apps/web` and fill in the required values.
2. Ensure you have Supabase running or a remote Supabase instance set up.
3. Run `docker-compose up -d` from the root directory to start the Redis and FastAPI/Celery workers.

## Important Features

- **Asynchronous Processing**: Incoming WhatsApp webhooks immediately enqueue a job in Redis via Celery to avoid blocking.
- **AI Orchestrator**: Uses Claude to detect intent, fetch necessary context and geo data, produce structured JSON insights, and translate to Gujarati.
- **Memory Layer**: Maintains `farmer_context` across sessions to contextualize crop types, common issues, etc.
- **Geocoding Normalization**: Resolves variations in village names to consistent GPS coordinates.
- **Prompt Versioning**: Tracks prompt templates and AI model versions.