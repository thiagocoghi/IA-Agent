import { supabase } from './lib/supabase.js'

// --- 1. DETECÇÃO DE AMBIENTE E ROTEAMENTO ---
const path = window.location.pathname;
const isLoginPage = path.endsWith('index.html') || path === '/' || (path.endsWith('.html') === false && !path.includes('dashboard') && !path.includes('cadastro'));
const isCadastroPage = path.includes('cadastro.html');
const isDashboardPage = path.includes('dashboard.html');

console.log(`[Ambiente] Login: ${isLoginPage} | Cadastro: ${isCadastroPage} | Dashboard: ${isDashboardPage}`);

// --- 2. SEGURANÇA E GESTÃO DE SESSÃO (Gatekeeper) ---
supabase.auth.onAuthStateChange((event, session) => {
    console.log(`[Auth Event] ${event}`);

    if (event === 'SIGNED_IN' && (isLoginPage || isCadastroPage)) {
        console.log("Usuário autenticado, redirecionando para Dashboard...");
        window.location.href = 'dashboard.html';
    }

    if (event === 'SIGNED_OUT' && isDashboardPage) {
        console.log("Sessão encerrada, voltando para Login...");
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

            if (!email || !password) {
                alert("⚠️ Por favor, preencha todos os campos para entrar.");
                return;
            }

            console.log("Tentando login para:", email);
            const { error } = await supabase.auth.signInWithPassword({ email, password });

            if (error) {
                console.error("Erro no login:", error.message);
                alert("❌ Erro de autenticação: " + error.message);
            }
        };
    }
}

// --- 4. LÓGICA DA PÁGINA DE CADASTRO ---
if (isCadastroPage) {
    const formCad = document.getElementById('form-cadastro');
    if (formCad) {
        formCad.onsubmit = async (e) => {
            e.preventDefault();

            const nome = document.getElementById('cad-nome').value;
            const empresa = document.getElementById('cad-empresa').value;
            const email = document.getElementById('cad-email').value;
            const password = document.getElementById('cad-password').value;

            if (!nome || !empresa || !email || !password) {
                alert("⚠️ Todos os campos são obrigatórios para o cadastro.");
                return;
            }

            if (password.length < 6) {
                alert("⚠️ Por segurança, a senha deve ter pelo menos 6 caracteres.");
                return;
            }

            console.log("Iniciando processo de cadastro via Auth + Trigger...");

            // Aqui o signUp envia os metadados que a sua Trigger SQL usa para criar a Empresa e o Perfil
            const { data, error: authError } = await supabase.auth.signUp({
                email,
                password,
                options: {
                    data: {
                        full_name: nome,
                        company_name: empresa
                    }
                }
            });

            if (authError) {
                console.error("Erro no cadastro Auth:", authError.message);
                alert("❌ Erro ao criar conta: " + authError.message);
                return;
            }

            if (data.user) {
                console.log("Usuário criado com sucesso. ID:", data.user.id);
                alert("✅ Cadastro realizado com sucesso! Sua clínica e perfil estão sendo configurados.");
            }
        };
    }
}

// --- 5. LÓGICA DO DASHBOARD ---
if (isDashboardPage) {
    const btnLogout = document.getElementById('btn-logout');
    const btnAgenda = document.getElementById('btn-agenda');
    const btnEquipe = document.getElementById('btn-equipe');
    const btnAddProf = document.getElementById('btn-add-prof');

    if (btnLogout) btnLogout.onclick = () => {
        console.log("Encerrando sessão...");
        supabase.auth.signOut();
    };

    if (btnAgenda) btnAgenda.onclick = () => switchTab('agenda');
    if (btnEquipe) btnEquipe.onclick = () => switchTab('equipe');
    if (btnAddProf) btnAddProf.onclick = addProfissional;

    // Inicialização do Dashboard
    console.log("Carregando dados iniciais do Dashboard...");
    loadAgenda();
}

// --- 6. FUNÇÕES AUXILIARES E INTERFACE ---

function switchTab(tabId) {
    console.log(`Alternando para aba: ${tabId}`);
    const tabs = document.querySelectorAll('.tab-content');
    const btns = document.querySelectorAll('nav button');

    tabs.forEach(t => t.classList.remove('active'));
    btns.forEach(b => b.classList.remove('active'));

    const targetTab = document.getElementById('tab-' + tabId);
    const targetBtn = document.getElementById('btn-' + tabId);

    if (targetTab && targetBtn) {
        targetTab.classList.add('active');
        targetBtn.classList.add('active');
    }

    if (tabId === 'equipe') loadProfissionais();
    if (tabId === 'agenda') loadAgenda();
}

async function addProfissional() {
    const inputNome = document.getElementById('prof-nome');
    const inputEspec = document.getElementById('prof-especialidade');

    if (!inputNome) return;
    const nome = inputNome.value.trim();
    const especialidade = inputEspec ? inputEspec.value.trim() || 'Geral' : 'Geral';

    if (!nome) {
        alert("⚠️ Por favor, digite o nome do profissional.");
        return;
    }

    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) {
        alert("❌ Erro de sessão: Usuário não identificado.");
        return;
    }

    console.log("Cadastrando profissional para o usuário:", user.id);
    const { error } = await supabase.from('profissionais').insert([{
        nome: nome,
        especialidade: especialidade,
        user_id: user.id
    }]);

    if (error) {
        console.error("Erro ao salvar profissional:", error.message);
        alert("❌ Erro ao cadastrar no banco: " + error.message);
    } else {
        alert("✅ " + nome + " cadastrado com sucesso!");
        inputNome.value = '';
        if (inputEspec) inputEspec.value = '';
        loadProfissionais();
    }
}

async function loadProfissionais() {
    const lista = document.getElementById('lista-prof');
    if (!lista) return;

    console.log("Buscando lista de profissionais...");
    const { data, error } = await supabase.from('profissionais').select('*');

    if (error) {
        console.error("Erro ao carregar profissionais:", error.message);
        alert("❌ Não foi possível carregar a lista de profissionais.");
        return;
    }

    if (data) {
        lista.innerHTML = data.map(p => `
            <li class="item-lista">
                <strong>👤 ${p.nome}</strong> - <small>${p.especialidade}</small>
            </li>
        `).join('');
    }
}

async function loadAgenda() {
    const container = document.getElementById('lista-agenda');
    if (!container) return;

    console.log("Buscando agendamentos do dia...");
    const { data, error } = await supabase.from('agendamentos').select('*');

    if (error) {
        console.error("Erro ao carregar agenda:", error.message);
        alert("❌ Erro ao buscar agendamentos.");
        return;
    }

    if (data && data.length > 0) {
        container.innerHTML = data.map(a => `
            <div class="card-agendamento">
                <strong>⏰ ${a.hora}</strong> - ${a.cliente_nome}
            </div>
        `).join('');
    } else {
        container.innerHTML = "<p class='msg-vazia'>Nenhum agendamento para hoje.</p>";
    }
}