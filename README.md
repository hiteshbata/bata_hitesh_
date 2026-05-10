# GujBot

Multi-Provider AI Assistant for Gujarati Businesses.

## Setup Instructions

### 1. Create Telegram Bot
1. Go to Telegram and message `@BotFather`.
2. Use `/newbot` to create your bot and get the `TELEGRAM_BOT_TOKEN`.
3. Message `@userinfobot` to get your `ADMIN_TELEGRAM_ID`.

### 2. Database Setup (Supabase)
1. Create a Supabase project.
2. Go to the SQL Editor and run:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE business_docs (
  id BIGSERIAL PRIMARY KEY,
  business_id TEXT NOT NULL,
  content TEXT NOT NULL,
  embedding VECTOR(1536),
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ON business_docs USING ivfflat (embedding vector_cosine_ops);

-- Create the match_business_docs function for RAG search
CREATE OR REPLACE FUNCTION match_business_docs (
  query_embedding VECTOR(1536),
  filter_business_id TEXT,
  match_threshold FLOAT,
  match_count INT
) RETURNS TABLE (
  id BIGINT,
  business_id TEXT,
  content TEXT,
  similarity FLOAT
) LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT
    business_docs.id,
    business_docs.business_id,
    business_docs.content,
    1 - (business_docs.embedding <=> query_embedding) AS similarity
  FROM business_docs
  WHERE business_docs.business_id = filter_business_id
    AND 1 - (business_docs.embedding <=> query_embedding) > match_threshold
  ORDER BY business_docs.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```
##replace any mentions of gemini-2.0-flash with the new gemini-3-flash-preview model.

### 3. API Keys
*   Get OpenAI API Key (Required for embeddings).
*   Get Google Generative AI Key or OpenRouter API Key (for LLM).

### 4. Local Setup
```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in your .env values!
```

### 5. Upload Sample Docs
```bash
python embeddings.py --business_id="mehta_jewellers" --file="docs/sample_jewelry_shop.txt"
```

### 6. Run Bot
Set `MODE=polling` in your `.env` for local testing.
```bash
python main.py
```

### Cheapest MVP Testing Setup
For zero cost MVP testing use:
- Embeddings: OpenAI ($5 free credit lasts months)
- AI Model: Google Gemini 2.0 Flash (free tier) OR OpenRouter Llama 3.3 70B (free tier)
- Use `/switchmodel` to test which gives best Gujarati.
