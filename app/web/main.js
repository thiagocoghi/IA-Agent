import { supabase } from './lib/services/supabase.js'

// --- 1. DETECÇÃO DE AMBIENTE E ROTEAMENTO ---
const path = window.location.pathname;
const isLoginPage = path.endsWith('index.html') || path === '/' || (!path.includes('dashboard') && !path.includes('cadastro'));
const isDashboardPage = path.includes('dashboard.html');
const isCadastroPage = path.includes('cadastro.html');

console.log(`[Main] Contexto: ${isLoginPage ? 'Login' : isDashboardPage ? 'Dashboard' : 'Outros'}`);

// --- 2. SEGURANÇA E GESTÃO DE SESSÃO GLOBAL ---
supabase.auth.onAuthStateChange((event, session) => {
    console.log(`[Auth Event] ${event}`);

    if (event === 'SIGNED_IN' && (isLoginPage || isCadastroPage)) {
        window.location.href = 'dashboard.html';
    }

    if (event === 'SIGNED_OUT' && isDashboardPage) {
        window.location.href = 'index.html';
    }
});

// --- 3. LÓGICA DA PÁGINA DE LOGIN ---
if (isLoginPage) {
    const btnLogin = document.getElementById('btn-login');
    if (btnLogin) {
        btnLogin.onclick = async (e) => {
            e.preventDefault();
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;

            if (!email || !password) return alert("⚠️ Preencha e-mail e senha.");

            const { error } = await supabase.auth.signInWithPassword({ email, password });
            if (error) alert("❌ Erro: " + error.message);
        };
    }
}

// --- 4. LÓGICA DO DASHBOARD ---
if (isDashboardPage) {
    const btnLogout = document.getElementById('btn-logout');
    const btnAgenda = document.getElementById('btn-agenda');
    const btnEquipe = document.getElementById('btn-equipe');
    const btnAddProf = document.getElementById('btn-add-prof');

    if (btnLogout) btnLogout.onclick = () => supabase.auth.signOut();
    if (btnAgenda) btnAgenda.onclick = () => switchTab('agenda');
    if (btnEquipe) btnEquipe.onclick = () => switchTab('equipe');
    if (btnAddProf) btnAddProf.onclick = addProfissional;

    loadAgenda();
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.toggle('active', t.id === `tab-${tabId}`));
    document.querySelectorAll('nav button').forEach(b => b.classList.toggle('active', b.id === `btn-${tabId}`));

    if (tabId === 'equipe') loadProfissionais();
    if (tabId === 'agenda') loadAgenda();
}

async function addProfissional() {
    const inputNome = document.getElementById('prof-nome');
    const nome = inputNome?.value.trim();
    if (!nome) return alert("⚠️ O nome é obrigatório.");

    const { data: { user } } = await supabase.auth.getUser();
    const { error } = await supabase.from('profissionais').insert([{ nome, user_id: user.id }]);

    if (error) alert("❌ Erro ao salvar.");
    else {
        alert("✅ Sucesso!");
        inputNome.value = '';
        loadProfissionais();
    }
}

async function loadProfissionais() {
    const lista = document.getElementById('lista-prof');
    if (!lista) return;
    const { data, error } = await supabase.from('profissionais').select('*');
    if (data) {
        lista.innerHTML = data.map(p => `<li>${p.nome}</li>`).join('');
    }
}

async function loadAgenda() {
    const container = document.getElementById('lista-agenda');
    if (!container) return;
    const { data } = await supabase.from('agendamentos').select('*');
    container.innerHTML = data?.length > 0 ? data.map(a => `<div>${a.cliente_nome}</div>`).join('') : "Vazio";
}