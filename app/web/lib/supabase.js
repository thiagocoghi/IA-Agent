import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm'

// --- CONFIGURAÇÃO ÚNICA (Não duplicar estas variáveis) ---

// 1. Tenta ler do ambiente (Vite)
// 2. Se falhar (undefined), usa os valores reais como Fallback
const supabaseUrl = import.meta.env?.VITE_SUPABASE_URL || 'https://ycbibzsnkebqpdhzfxqk.supabase.co'
const supabaseKey = import.meta.env?.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InljYmlienNua2VicXBkaHpmeHFrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3MDk5ODQsImV4cCI6MjA5MDI4NTk4NH0.hD1uDEk9Xh-PZaGYfjNt--1MMXcDVDvcvxUFasZ-p9k'

// Log de depuração para o seu Console (F12)
console.log("🔗 Conexão Supabase inicializada com sucesso.");

// Exportação única do cliente
export const supabase = createClient(supabaseUrl, supabaseKey)