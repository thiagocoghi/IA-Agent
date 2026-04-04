// 1. CONFIGURAÇÃO - Substitua pelos seus dados REAIS do painel
const SUPABASE_URL = 'https://ycbibzsnkebqpdhzfxqk.supabase.co';
const SUPABASE_KEY = 'AIzaSyDdIwRQesih7ViJySFc3p_t1biR1XLVRRE';

let _supabase;

// Função que inicializa o cliente com segurança
function iniciarSupabase() {
    if (window.supabase) {
        _supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
        console.log("✅ Supabase carregado e inicializado!");

        // Só vincula os botões DEPOIS que o Supabase existe
        document.getElementById('btnEntrar').onclick = realizarLogin;
        document.getElementById('btnBuscar').onclick = buscarDados;
    } else {
        console.error("❌ Erro: A biblioteca do Supabase ainda não carregou.");
        setTimeout(iniciarSupabase, 500); // Tenta de novo em meio segundo
    }
}

// 2. LOGICA DE LOGIN
async function realizarLogin() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    console.log("Tentando login...");
    const { data, error } = await _supabase.auth.signInWithPassword({
        email: email,
        password: password
    });

    if (error) {
        document.getElementById('status').innerText = "Erro: " + error.message;
        alert("Falha: " + error.message);
    } else {
        document.getElementById('status').innerText = "Logado como: " + data.user.email;
        alert("Sucesso! Agora teste a busca.");
    }
}

async function buscarDados() {
    const { data, error } = await _supabase.from('agendamentos').select('*');
    if (error) {
        document.getElementById('resultado').innerText = "Erro RLS: " + error.message;
    } else {
        document.getElementById('resultado').innerText = JSON.stringify(data, null, 2);
    }
}

// Inicia a verificação assim que a página abrir
window.onload = iniciarSupabase;