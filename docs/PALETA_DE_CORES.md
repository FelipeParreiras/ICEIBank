# Paleta de cores do ICEIBank

## Objetivo

A identidade do ICEIBank usa verde como base de confiança e continuidade,
superfícies claras esverdeadas para leitura e dourado para chamar atenção a
estados relevantes. O objetivo é reduzir grandes áreas brancas sem prejudicar o
contraste de formulários, dados financeiros e ações críticas.

## Verdes de identidade

| Token | Hexadecimal | Uso |
|---|---|---|
| `--green-dark` | `#0D3C2A` | Fundo profundo, títulos em superfícies claras e contraste forte |
| `--green` | `#175C3A` | Fundo principal da aplicação, ação primária e opção selecionada |
| `--green-medium` | `#5A8F74` | Bordas ativas, ícones e apoio visual |
| `--green-pastel` | `#EAF2EC` | Hover, seleção suave e superfícies de apoio |
| `--green-soft` | `#F3F8F4` | Cartões, menus, formulários e superfícies secundárias |

## Dourados de destaque

| Token | Hexadecimal | Uso |
|---|---|---|
| `--gold-dark` | `#8C671D` | Texto de destaque e detalhes de ícone |
| `--gold` | `#C59A3C` | Destaque principal, progresso e prioridade |
| `--gold-pastel` | `#E1CC79` | Ênfase suave em fundos escuros |
| `--gold-soft` | `#FFF2D8` | Fundo de ícones, recomendações e controles auxiliares |

## Neutros de interface

| Token | Hexadecimal | Uso |
|---|---|---|
| texto principal | `#17211C` | Conteúdo e títulos em superfícies claras |
| `--muted` | `#6B756F` | Descrições e informação secundária |
| `--line` | `#DCE4DE` | Bordas e divisores |
| `--cream` | `#F7F7EF` | Superfície de equilíbrio e leitura |
| branco | `#FFFFFF` | Apenas texto sobre fundo escuro e situações pontuais de alto contraste |

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

## Implementação

Os tokens ficam em [global.css](../frontend/src/styles/global.css). Componentes
novos devem consumir esses tokens, sem introduzir hexadecimais concorrentes.
O [SelectField](../frontend/src/components/SelectField.jsx) concentra o padrão
visual e de interação dos menus de seleção.
