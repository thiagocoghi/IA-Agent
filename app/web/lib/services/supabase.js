import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm'

// Use fallback direto para evitar falhas de análise do 'import.meta.env' em alguns navegadores
const supabaseUrl = 'https://ycbibzsnkebqpdhzfxqk.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InljYmlienNua2VicXBkaHpmeHFrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3MDk5ODQsImV4cCI6MjA5MDI4NTk4NH0.hD1uDEk9Xh-PZaGYfjNt--1MMXcDVDvcvxUFasZ-p9k'

export const supabase = createClient(supabaseUrl, supabaseKey)
console.log("🔗 Banco de dados conectado.");