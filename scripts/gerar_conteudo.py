"""
gerar_conteudo.py
─────────────────
Gera roteiro de curiosidade bíblica (aprox 180–220 palavras)
usando a API Groq (llama-3.3-70b-versatile).

O roteiro é criado a partir do gancho e categoria sorteados.
"""

import os
import json

from groq import Groq

# ─────────────────────────────────────────────────────────────────────────────
# Geração principal
# ─────────────────────────────────────────────────────────────────────────────
def gerar_conteudo(tema_info: dict) -> dict:
    """
    Gera o roteiro narrativo baseado no tema sorteado.

    Parâmetros:
        tema_info — dict retornado por sortear_tema()

    Retorna dict com:
        oracao_texto (reaproveitando o nome do campo para o roteiro),
        titulo, descricao, tags, categoria
    """
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    gancho = tema_info["gancho"]
    categoria = tema_info["categoria"]

    prompt = f"""Você é um Narrador Especialista em Curiosidades e Mistérios Bíblicos que grava roteiros para o YouTube Shorts (estilo documentário curto, envolvente, de mistério e choque).

Crie um ROTEIRO CURTO para um vídeo da categoria "{categoria}" usando o gancho abaixo como frase de abertura.

GANCHO OBRIGATÓRIO (primeira frase do vídeo):
"{gancho}"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ESTRUTURA OBRIGATÓRIA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. O GANCHO E A INTRODUÇÃO (1 parágrafo curto):
   - Comece EXATAMENTE com a frase: "{gancho}"
   - Adicione uma ou duas frases criando suspense e curiosidade sobre o assunto.

2. O DESENVOLVIMENTO DO MISTÉRIO/FATO (2 a 3 parágrafos curtos):
   - Explique o fato histórico, o mito desvendado, a curiosidade arqueológica ou profecia.
   - Use um tom de revelação de um segredo oculto ou algo impressionante.
   - Seja direto e claro, sem enrolação.

3. CONCLUSÃO E CHAMADA DE AÇÃO (1 parágrafo curto):
   - Dê uma conclusão de impacto que deixe o espectador pensando.
   - Faça uma chamada de ação rápida e natural: "Gostou desse mistério? Se inscreve no canal para mais curiosidades bíblicas."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REGRAS OBRIGATÓRIAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- MÍNIMO 180 palavras, MÁXIMO 220 palavras (muito importante para caber em 1 minuto de áudio TTS!)
- Tom: Documentário, misterioso, envolvente, direto.
- Linguagem: português brasileiro formal-popular
- SEM markdown, asteriscos, negritos ou formatação — apenas texto puro para ser lido pelo sintetizador de voz.
- Parágrafos separados por linha em branco.

Ao final do texto do roteiro, adicione exatamente esta linha separadora e o JSON:

---JSON---
{{
  "titulo": "{gancho} 🤯 | #CuriosidadesBiblicas #Shorts",
  "descricao": "Você sabia disso? 📖 Descubra hoje mais sobre {categoria} neste vídeo! Inscreva-se para mais segredos e fatos ocultos da Bíblia. #Shorts #CuriosidadesBiblicas #Misterios #Teologia",
  "tags": ["Shorts", "curiosidades", "bíblia", "mistérios da bíblia", "teologia", "história bíblica", "arqueologia bíblica", "fatos ocultos"]
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.75,
        max_tokens=1024,
    )

    content = response.choices[0].message.content.strip()

    # Separar texto do roteiro do JSON
    if "---JSON---" in content:
        partes = content.split("---JSON---", 1)
        oracao_texto = partes[0].strip()
        try:
            metadata = json.loads(partes[1].strip())
        except json.JSONDecodeError:
            metadata = _metadata_padrao(tema_info)
    else:
        oracao_texto = content
        metadata = _metadata_padrao(tema_info)

    metadata["oracao_texto"]    = oracao_texto
    metadata["categoria"]       = categoria
    metadata["gancho"]          = gancho
    
    # Preencher campos legados que o pipeline atual possa exigir para evitar quebras
    metadata["versiculo_texto"] = "" 
    metadata["versiculo_ref"]   = ""

    palavras = len(oracao_texto.split())
    print(f"✅ Roteiro gerado: {palavras} palavras")
    print(f"   Categoria : {categoria}")

    return metadata


def _metadata_padrao(tema_info: dict) -> dict:
    gancho = tema_info["gancho"]
    categoria = tema_info["categoria"]
    return {
        "titulo":    f"{gancho} 🤯 | #CuriosidadesBiblicas #Shorts",
        "descricao": (
            f"Você sabia disso? 📖 Descubra hoje mais sobre {categoria} neste vídeo!\n"
            f"Inscreva-se para mais segredos e fatos ocultos da Bíblia. #Shorts #CuriosidadesBiblicas"
        ),
        "tags": [
            "Shorts", "curiosidades", "bíblia", "mistérios", "história bíblica",
        ],
    }


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scripts.sortear_tema import sortear_tema

    os.makedirs("output", exist_ok=True)
    info = sortear_tema()
    resultado = gerar_conteudo(info)

    with open("output/conteudo.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Conteúdo salvo em output/conteudo.json")
    print(f"   Título: {resultado['titulo']}")
