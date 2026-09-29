import { useEffect, useState } from "react";

import { AGENCIAS, apiRequest } from "../api/cliente";
import { mensagemAmigavel } from "../api/erros";

export function useContas(agenciaId, token) {
  const [versao, setVersao] = useState(0);
  const [resultado, setResultado] = useState(null);
  const chave = `${agenciaId}:${token}:${versao}`;

  useEffect(() => {
    let ativo = true;
    Promise.allSettled(AGENCIAS.map(async (agencia) => {
      const contas = await apiRequest("/contas", { agenciaId: agencia.id, token });
      return contas.map((conta) => ({ ...conta, agenciaId: agencia.id }));
    }))
      .then((respostas) => {
        const contas = respostas.flatMap((resposta) => resposta.status === "fulfilled" ? resposta.value : []);
        const erros = respostas.flatMap((resposta, index) => resposta.status === "rejected"
          ? [`${AGENCIAS[index].nome}: ${mensagemAmigavel(resposta.reason)}`] : []);
        if (ativo) setResultado({ chave, contas, erro: erros.join(" ") });
      });
    return () => { ativo = false; };
  }, [agenciaId, token, chave]);

  const atualizado = resultado?.chave === chave;
  return {
    contas: atualizado ? resultado.contas : [],
    carregando: !atualizado,
    erro: atualizado ? resultado.erro : "",
    atualizar: () => setVersao((atual) => atual + 1),
  };
}
