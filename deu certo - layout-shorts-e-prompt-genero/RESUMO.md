# ✅ Deu Certo — Layout do Shorts e Correção de Gênero no Prompt

**Data:** 2026-06-29
**Projeto:** Canal Oração Shorts

## O que funcionou

Ajustamos o layout vertical (9:16) no FFmpeg removendo completamente os fundos pretos sólidos e os textos de versículos da tela inicial, deixando apenas as legendas SRT da locução por cima da imagem natural. Para não perder legibilidade, passamos a usar `BorderStyle=1` nas legendas com `Shadow=3` e `Outline=2`, gerando letras limpas com sombreamento. Além disso, corrigimos um erro gramatical que o LLM cometia ao narrar o período ("este noite"), ajustando o prompt base de "este(a)" para "esta", já que as palavras manhã, tarde e noite são femininas.

## Arquivos envolvidos

| Arquivo | Papel na solução |
|---------|-----------------|
| `montar_video.py` | Recebeu as remoções das funções de renderização do versículo em tela. Além disso, alterou a variável `subtitle_style` para evitar os quadros pretos de fundo. |
| `gerar_conteudo.py` | Modificou o prompt `"{saudacao}! Que Deus abençoe esta {descricao} na sua vida."` para não confundir o modelo sobre a concordância nominal de gênero. |

## Como replicar

1. Para legendas flutuantes e limpas num fundo escuro/natureza no formato vertical: evite caixas sólidas, utilize no FFmpeg o filtro `subtitles` passando o parâmetro `force_style='BorderStyle=1,Shadow=3,Outline=2'`.
2. Em prompts de locução em Português gerados por IA, certifique-se de forçar artigos definidos corretos se o contexto usar variáveis que são exclusivamente masculinas ou femininas, pois abstrações como "este(a)" levam a erros aleatórios do LLM.

## Observações

Ao lidar com `subtitles` + FFmpeg, a escala da legenda (FontSize) é baseada em uma proporção base do renderer interno (384x288), e não necessariamente 1:1 na proporção em pixels (1080x1920). Por isso o FontSize=18 funcionou perfeitamente e não explodiu na tela.
