import { authService } from './lib/services/authServices.js'

const formCad = document.getElementById('form-cadastro');

if (formCad) {
    formCad.onsubmit = async (e) => {
        e.preventDefault();

        const btnSubmit = formCad.querySelector('button');
        const nome = document.getElementById('cad-nome').value;
        const empresa = document.getElementById('cad-empresa').value;
        const email = document.getElementById('cad-email').value;
        const password = document.getElementById('cad-password').value;

        try {
            btnSubmit.disabled = true;
            btnSubmit.innerText = "Processando...";

            await authService.cadastrarNovoUsuario(email, password, nome, empresa);

            alert("✅ Conta criada com sucesso!");
            window.location.href = 'index.html';
        } catch (error) {
            console.error("Erro no fluxo de cadastro:", error);
            alert("❌ Falha no cadastro: " + (error.message || "Erro desconhecido"));
        } finally {
            btnSubmit.disabled = false;
            btnSubmit.innerText = "Finalizar Cadastro";
        }
    };
}