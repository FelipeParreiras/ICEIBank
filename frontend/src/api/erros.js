export class ApiError extends Error {
  constructor({ status = null, codigo, mensagem, detalhes = null, tipo = "negocio" }) {
    super(mensagem);
    this.name = "ApiError";
    this.status = status;
    this.codigo = codigo;
    this.detalhes = detalhes;
    this.tipo = tipo;
  }
}

export function mensagemAmigavel(error) {
  const mensagens = {
    CREDENCIAIS_INVALIDAS: "Usuário ou senha inválidos.",
    USUARIO_JA_EXISTE: "Este usuário já está cadastrado. Escolha outro nome ou entre na sua conta.",
    AUTENTICACAO_INDISPONIVEL: "Não foi possível acessar o serviço de autenticação. Tente novamente.",
    TOKEN_EXPIRADO: "Sua sessão expirou. Entre novamente.",
    CONTA_NAO_ENCONTRADA: "Conta não encontrada na agência selecionada.",
    CONTA_FORA_DA_PARTICAO: "Essa conta pertence a outra agência.",
    SALDO_INSUFICIENTE: "Saldo insuficiente para concluir a operação.",
    AGENCIA_DESTINO_INDISPONIVEL:
      "A agência de destino não respondeu. Atenção: o débito da origem foi aplicado.",
    PLANEJAMENTO_NAO_ENCONTRADO: "Defina o planejamento desse mês antes de registrar gastos.",
  };
  return mensagens[error?.codigo] || error?.message || "Não foi possível concluir a operação.";
}
