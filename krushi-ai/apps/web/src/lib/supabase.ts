import { createClient } from '@supabase/supabase-js';

// Provide explicit fallback values so the client doesn't crash during build or if .env is missing.
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'http://localhost:54321';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'ey_dummy_key_for_build';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
