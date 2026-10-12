# Paleta de cores do ICEIBank

## Objetivo

A identidade do ICEIBank usa verde como base de confiança e continuidade,
superfícies claras esverdeadas para leitura e dourado para chamar atenção a
estados relevantes. O objetivo é reduzir grandes áreas brancas sem prejudicar o
contraste de formulários, dados financeiros e ações críticas.

## Leitura rápida

O visual do ICEIBank é organizado em três camadas: verde para identidade e
ações principais, dourado para chamar atenção a informações financeiras e
neutros para tornar textos, bordas e superfícies legíveis. Os nomes abaixo são
os nomes de design; os tokens são a referência a ser usada no CSS.

## Verdes de identidade

| Nome visual | Token | Hexadecimal | Uso |
|---|---|---|
| Verde profundo | `--green-dark` | `#0D3C2A` | Fundo profundo, títulos em superfícies claras e contraste forte |
| Verde ICEI | `--green` | `#175C3A` | Fundo principal da aplicação, ação primária e opção selecionada |
| Verde sálvia | `--green-medium` | `#5A8F74` | Bordas ativas, ícones e apoio visual |
| Verde névoa | `--green-pastel` | `#EAF2EC` | Hover, seleção suave e superfícies de apoio |
| Menta clara | `--green-soft` | `#F3F8F4` | Cartões, menus, formulários e superfícies secundárias |

## Dourados de destaque

| Nome visual | Token | Hexadecimal | Uso |
|---|---|---|
| Ouro profundo | `--gold-dark` | `#8C671D` | Texto de destaque e detalhes de ícone |
| Ouro ICEI | `--gold` | `#C59A3C` | Destaque principal, progresso e prioridade |
| Dourado pastel | `--gold-pastel` | `#E1CC79` | Ênfase suave em fundos escuros |
| Dourado de painel | `--gold-panel` | `#DFC779` | Fundo da área de acesso, em contraste com a marca verde |
| Creme dourado | `--gold-soft` | `#FFF2D8` | Fundo de ícones, recomendações e controles auxiliares |
| Creme neutro | — | `#F7F7EF` | Equilíbrio visual em áreas de leitura e fundos claros |

## Neutros de interface

| Nome visual | Token | Hexadecimal | Uso |
|---|---|---|
| Texto principal | — | `#17211C` | Conteúdo e títulos em superfícies claras |
| Texto secundário | `--muted` | `#6B756F` | Descrições e informação secundária |
| Linha suave | `--line` | `#DCE4DE` | Bordas e divisores |
| Fundo geral | `--cream` | `#F7F7EF` | Superfície de equilíbrio e leitura |
| Superfície elevada | — | `#FFFFFF` | Uso pontual em alto contraste; não é o fundo dominante da aplicação |

## Hierarquia de uso

| Elemento | Cor predominante | Papel visual |
|---|---|---|
| Fundo externo e áreas de marca | Verde profundo e Verde ICEI | Define identidade, profundidade e continuidade visual |
| Área de acesso | Dourado de painel | Separa visualmente o formulário da área institucional sem recorrer ao branco |
| Painéis, cards e modais | Menta clara e Verde névoa | Mantém a leitura leve sem recorrer a grandes blocos brancos |
| Campos e opções de seleção | Menta clara, borda Verde sálvia | Indica interação sem competir com a ação principal |
| Ações primárias e opção selecionada | Verde ICEI com texto branco | Evidencia a ação que confirma ou altera dados |
| Progresso, prioridade e recomendações | Ouro ICEI e Creme dourado | Direciona atenção para informação financeira relevante |
| Estados semânticos | Cores específicas de sucesso, aviso e erro | Comunicam resultado; não devem ser substituídas pelo dourado |

## Regras de aplicação

- O fundo da aplicação combina `#0D3C2A`, `#175C3A` e verde médio em gradiente.
- Painéis, modais, menus e cartões usam verde-pastel ou verde suave; não devem
  criar blocos brancos extensos.
- O dourado sinaliza foco visual, prioridade, recomendação ou estado ativo; não
  substitui cores semânticas de sucesso, aviso e erro.
- O componente `SelectField` usa menu próprio: borda de `10px`, opções com
  `8px`, verde para a seleção e dourado na seta. Isso evita que o menu do
  sistema operacional imponha a seleção azul padrão.
- Cor nunca é a única forma de explicar um estado: rótulos, ícones e texto
  continuam necessários.

## Contraste e manutenção

- Em superfícies claras, priorizar `#17211C` ou `--green-dark` para texto
  principal e `--muted` apenas em conteúdo complementar.
- Texto branco deve aparecer sobre `--green`, `--green-dark` ou outro fundo
  escuro equivalente. Não usar branco para texto comum em superfícies claras.
- Antes de adicionar um hexadecimal, verificar se um token existente cumpre o
  mesmo papel. Novos tokens devem ser criados em `:root`, documentados aqui e
  nomeados pelo seu papel, não por uma tela específica.
- Estados de foco devem combinar borda Verde sálvia e anel translúcido, para
  preservar a navegação por teclado sem introduzir a seleção azul nativa.

## Implementação

Os tokens ficam em [global.css](../frontend/src/styles/global.css). Componentes
novos devem consumir esses tokens, sem introduzir hexadecimais concorrentes.
O [SelectField](../frontend/src/components/SelectField.jsx) concentra o padrão
visual e de interação dos menus de seleção.
