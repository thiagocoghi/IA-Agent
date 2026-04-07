import { supabase } from './supabase.js'

export const authService = {
    async cadastrarNovoUsuario(email, password, nome, empresaNome) {
        // PASSO ÚNICO: Criar o usuário no Auth enviando metadados
        // Esses metadados (full_name e company_name) são lidos pela Trigger no SQL
        const { data: authData, error: authError } = await supabase.auth.signUp({
            email,
            password,
            options: {
                data: {
                    full_name: nome,
                    company_name: empresaNome
                }
            }
        });

        if (authError) {
            console.error("Erro no Auth SignUp:", authError.message);
            throw authError;
        }

        // NOTA DE QA: Não precisamos fazer NENHUM .insert() aqui embaixo.
        // A Trigger on_auth_user_created já criou a Empresa e o Perfil no banco
        // assim que o comando acima foi finalizado com sucesso.

        return authData.user;
    }
};