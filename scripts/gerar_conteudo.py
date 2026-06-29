"""
gerar_conteudo.py
─────────────────
Gera oração curta (180–220 palavras) e versículo bíblico aleatório
adequado ao período do dia (bom dia / boa tarde / boa noite)
usando a API Groq (llama-3.3-70b-versatile).

A oração é temática e coerente com o versículo sorteado e o período.
"""

import os
import json
import random

from groq import Groq

# ─────────────────────────────────────────────────────────────────────────────
# Banco de versículos por período
# ─────────────────────────────────────────────────────────────────────────────
VERSICULOS = {
    "bom_dia": [
        {"ref": "Salmos 5:3",     "texto": "Pela manhã ouvirás a minha voz, ó Senhor; pela manhã apresentarei a minha oração a ti e esperarei."},
        {"ref": "Salmos 143:8",   "texto": "Faze-me ouvir a tua benignidade pela manhã, porque em ti confio; faze-me saber o caminho em que devo andar, porque a ti elevo a minha alma."},
        {"ref": "Lamentações 3:22-23", "texto": "As misericórdias do Senhor não têm fim, as suas bondades não têm limite. Renovam-se cada manhã; grande é a tua fidelidade."},
        {"ref": "Salmos 118:24",  "texto": "Este é o dia que o Senhor fez; regozijemo-nos e alegremo-nos nele."},
        {"ref": "Efésios 5:14",   "texto": "Por isso diz: Desperta, tu que dormes, e levanta-te dentre os mortos, e Cristo te iluminará."},
        {"ref": "Salmos 90:14",   "texto": "Sacia-nos pela manhã com a tua benignidade, para que cantemos de alegria e nos alegremos todos os nossos dias."},
        {"ref": "Isaías 50:4",    "texto": "O Senhor me deu língua de instruídos, para que eu saiba falar palavra oportuna ao cansado. Desperta-me de manhã em manhã, desperta-me para ouvir como os instruídos."},
        {"ref": "Marcos 1:35",    "texto": "De manhã bem cedo, ainda escuro, Jesus levantou-se e foi a um lugar deserto, e ali orava."},
        {"ref": "Salmos 59:16",   "texto": "Mas eu cantarei o teu poder e, pela manhã, exaltarei a tua bondade, porque tu és o meu alto refúgio e meu abrigo no dia da minha angústia."},
        {"ref": "Provérbios 8:17","texto": "Eu amo os que me amam, e os que me procuram de madrugada me acharão."},
        {"ref": "Salmos 30:5",    "texto": "Porque a sua ira dura um momento, mas no seu favor há vida; o choro pode durar uma noite, mas a alegria vem pela manhã."},
        {"ref": "Isaías 33:2",    "texto": "Senhor, tem misericórdia de nós; em ti esperamos. Sê o nosso braço todas as manhãs, e também a nossa salvação no tempo da angústia."},
        {"ref": "Salmos 92:1-2",  "texto": "Bom é render graças ao Senhor e cantar louvores ao teu nome, ó Altíssimo; anunciar de manhã a tua benignidade e cada noite a tua fidelidade."},
        {"ref": "Salmos 63:1",    "texto": "Ó Deus, tu és o meu Deus; eu te buscarei de madrugada; a minha alma tem sede de ti."},
        {"ref": "Sofonias 3:17",  "texto": "O Senhor, o teu Deus, está no meio de ti, poderoso para salvar; alegrar-se-á sobre ti com júbilo, renovar-te-á com o seu amor."},
    ],
    "boa_tarde": [
        {"ref": "Salmos 55:17",   "texto": "À tarde, pela manhã e ao meio-dia, orarei e clamarei, e ele ouvirá a minha voz."},
        {"ref": "Filipenses 4:7", "texto": "E a paz de Deus, que excede todo o entendimento, guardará os vossos corações e os vossos pensamentos em Cristo Jesus."},
        {"ref": "Isaías 40:31",   "texto": "Mas os que esperam no Senhor renovarão as suas forças, subirão com asas como águias; correrão e não se cansarão, caminharão e não se fatigarão."},
        {"ref": "Romanos 8:28",   "texto": "Sabemos que todas as coisas contribuem juntamente para o bem daqueles que amam a Deus, daqueles que são chamados segundo o seu propósito."},
        {"ref": "Jeremias 29:11", "texto": "Porque eu sei os planos que tenho para vocês, planos de fazê-los prosperar e não de causar dano, planos de dar a vocês esperança e um futuro."},
        {"ref": "Mateus 11:28",   "texto": "Vinde a mim, todos os que estais cansados e oprimidos, e eu vos aliviarei."},
        {"ref": "Filipenses 4:13","texto": "Posso tudo naquele que me fortalece."},
        {"ref": "Provérbios 3:5-6","texto": "Confia no Senhor de todo o teu coração e não te estribes no teu próprio entendimento. Reconhece-o em todos os teus caminhos, e ele endireitará as tuas veredas."},
        {"ref": "Salmos 46:1",    "texto": "Deus é o nosso refúgio e fortaleza, socorro bem presente na angústia."},
        {"ref": "João 14:27",     "texto": "Deixo-vos a paz, a minha paz vos dou; não vo-la dou como o mundo a dá. Não se turbe o vosso coração, nem se atemorize."},
        {"ref": "2 Coríntios 12:9","texto": "A minha graça te é suficiente, porque o poder se aperfeiçoa na fraqueza."},
        {"ref": "Salmos 37:5",    "texto": "Entrega o teu caminho ao Senhor; confia nele, e ele tudo fará."},
        {"ref": "Isaías 41:10",   "texto": "Não temas, porque eu sou contigo; não te assombres, porque eu sou o teu Deus; eu te fortaleço, e te ajudo, e te sustento com a minha destra fiel."},
        {"ref": "Efésios 3:20",   "texto": "Ora, àquele que é poderoso para fazer tudo muito mais abundantemente além daquilo que pedimos ou pensamos, segundo o poder que opera em nós."},
        {"ref": "Josué 1:9",      "texto": "Não to mandei eu? Sê forte e corajoso; não te atemorizes, nem te espantes, porque o Senhor, teu Deus, é contigo em qualquer lugar para onde deres."},
    ],
    "boa_noite": [
        {"ref": "Salmos 4:8",     "texto": "Em paz me deito e logo adormeço, pois só tu, Senhor, me fazes repousar em segurança."},
        {"ref": "Salmos 91:5",    "texto": "Não temerás o terror noturno, nem a seta que voa de dia."},
        {"ref": "Salmos 121:3-4", "texto": "Não deixará vacilar o teu pé; não dormitará aquele que te guarda. Eis que não dormitará nem dormirá o guarda de Israel."},
        {"ref": "Deuteronômio 31:6","texto": "Sê forte e corajoso; não temas, nem te espantes diante deles; porque o Senhor, teu Deus, é quem vai contigo; não te deixará, nem te desamparará."},
        {"ref": "Mateus 11:28",   "texto": "Vinde a mim, todos os que estais cansados e oprimidos, e eu vos aliviarei."},
        {"ref": "Salmos 127:2",   "texto": "É inútil que te levantes de madrugada e vás tarde para o repouso, comendo o pão com fadigas, pois assim dá Deus o sono ao seu amado."},
        {"ref": "João 14:1",      "texto": "Não se turbe o vosso coração. Credes em Deus; crede também em mim."},
        {"ref": "Salmos 34:4",    "texto": "Busquei o Senhor, e ele me respondeu; livrou-me de todos os meus temores."},
        {"ref": "Provérbios 3:24","texto": "Quando te deitares, não temerás; ao contrário, quando estiveres deitado, o teu sono será suave."},
        {"ref": "Salmos 23:4",    "texto": "Ainda que eu ande pelo vale da sombra da morte, não temerei mal algum, porque tu estás comigo; o teu cajado e o teu bordão me consolam."},
        {"ref": "Filipenses 4:6-7","texto": "Não andeis ansiosos por coisa alguma; antes em tudo fazei conhecidas as vossas petições a Deus em oração e súplica, com ações de graças. E a paz de Deus, que excede todo o entendimento, guardará os vossos corações e os vossos pensamentos em Cristo Jesus."},
        {"ref": "1 Pedro 5:7",    "texto": "Lançando sobre ele toda a vossa ansiedade, porque ele tem cuidado de vós."},
        {"ref": "Isaías 26:3",    "texto": "Tu conservarás em perfeita paz aquele cujo propósito está firme, porque em ti confia."},
        {"ref": "Salmos 3:5",     "texto": "Deitei-me e dormi; acordei, porque o Senhor me sustentou."},
        {"ref": "Números 6:24-26","texto": "O Senhor te abençoe e te guarde; o Senhor faça resplandecer o seu rosto sobre ti e tenha misericórdia de ti; o Senhor volte o seu rosto para ti e te conceda paz."},
        {"ref": "Salmos 16:7",    "texto": "Abençoarei o Senhor, que me aconselhou; até nas noites me ensinam os meus rins."},
        {"ref": "Salmos 77:6",    "texto": "Recordo o meu cântico de noite e medito no meu coração; e o meu espírito pesquisa."},
        {"ref": "Salmos 42:8",    "texto": "O Senhor ordenará a sua benignidade de dia, e de noite a sua canção estará comigo, oração ao Deus da minha vida."},
        {"ref": "Apocalipse 21:4","texto": "E Deus limpará de seus olhos toda lágrima, e não haverá mais morte, nem pranto, nem clamor, nem dor, porque já as primeiras coisas são passadas."},
        {"ref": "Salmos 139:12",  "texto": "Também as trevas não encobrem coisa alguma de ti, mas a noite resplandece como o dia; as trevas e a luz são para ti a mesma coisa."},
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# Geração principal
# ─────────────────────────────────────────────────────────────────────────────
def gerar_conteudo(periodo_info: dict) -> dict:
    """
    Gera oração curta + versículo para o período especificado.

    Parâmetros:
        periodo_info — dict retornado por detectar_periodo()

    Retorna dict com:
        oracao_texto, versiculo_texto, versiculo_ref,
        titulo, descricao, tags, periodo, saudacao
    """
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    periodo   = periodo_info["periodo"]
    saudacao  = periodo_info["saudacao"]
    emoji     = periodo_info["emoji"]
    descricao = periodo_info["descricao"]

    # Sorteia versículo aleatório para o período
    versiculo = random.choice(VERSICULOS[periodo])

    prompt = f"""Você é um pastor cristão evangélico brasileiro que grava mensagens de oração curtas para o YouTube Shorts no estilo do canal "Bispo Bruno Leonardo".

Crie uma ORAÇÃO CURTA de {saudacao.upper()} com base no versículo bíblico abaixo.

VERSÍCULO BASE:
"{versiculo['texto']}"
— {versiculo['ref']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ESTRUTURA OBRIGATÓRIA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. SAUDAÇÃO (1 parágrafo):
   - "{saudacao}! Que Deus abençoe este(a) {descricao} na sua vida."
   - Cite brevemente o versículo de {versiculo['ref']}

2. ORAÇÃO BREVE PODEROSA (3 parágrafos curtos):
   - Ore pelo período do dia ({descricao})
   - Use os nomes de Deus: Jeová Jiré, Jeová Shalom
   - Declare bênçãos específicas para o período ({descricao})
   - Relacione a oração com o tema do versículo

3. DECLARAÇÃO FINAL (1 parágrafo):
   - Uma declaração forte: "Eu decreto e declaro que..."
   - Encerramento: "Em nome de Jesus, Amém."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REGRAS OBRIGATÓRIAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- MÍNIMO 180 palavras, MÁXIMO 220 palavras (muito importante!)
- Tom: íntimo, pastoral, caloroso e cheio de fé
- Linguagem: português brasileiro formal-popular
- SEM markdown, asteriscos ou formatação — apenas texto puro
- Parágrafos separados por linha em branco

Ao final do texto da oração, adicione exatamente esta linha separadora e o JSON:

---JSON---
{{
  "titulo": "{emoji} Oração de {saudacao} — {versiculo['ref']} | Canal Oração #Shorts",
  "descricao": "🙏 {saudacao}! Receba esta oração especial baseada em {versiculo['ref']}. {versiculo['texto'][:80]}... Que Deus abençoe seu(ua) {descricao}! ❤️ Curta e compartilhe com alguém que precisa de fé. #Shorts #OraçãoDoDia #{saudacao.replace(' ', '')}",
  "tags": ["Shorts", "oração", "{saudacao.lower()}", "oração do dia", "versículo", "Canal Oração", "fé", "Deus", "Jesus", "bênção", "oração curta", "{versiculo['ref']}", "oração shorts"]
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.75,
        max_tokens=1024,
    )

    content = response.choices[0].message.content.strip()

    # Separar texto da oração do JSON
    if "---JSON---" in content:
        partes = content.split("---JSON---", 1)
        oracao_texto = partes[0].strip()
        try:
            metadata = json.loads(partes[1].strip())
        except json.JSONDecodeError:
            metadata = _metadata_padrao(periodo_info, versiculo)
    else:
        oracao_texto = content
        metadata = _metadata_padrao(periodo_info, versiculo)

    metadata["oracao_texto"]    = oracao_texto
    metadata["versiculo_texto"] = versiculo["texto"]
    metadata["versiculo_ref"]   = versiculo["ref"]
    metadata["periodo"]         = periodo
    metadata["saudacao"]        = saudacao

    palavras = len(oracao_texto.split())
    print(f"✅ Oração gerada: {palavras} palavras")
    print(f"   Versículo : {versiculo['ref']}")
    print(f"   Período   : {saudacao}")

    return metadata


def _metadata_padrao(periodo_info: dict, versiculo: dict) -> dict:
    saudacao  = periodo_info["saudacao"]
    descricao = periodo_info["descricao"]
    emoji     = periodo_info["emoji"]
    return {
        "titulo":    f"{emoji} Oração de {saudacao} — {versiculo['ref']} | Canal Oração #Shorts",
        "descricao": (
            f"🙏 {saudacao}! Receba esta oração especial baseada em {versiculo['ref']}.\n"
            f"{versiculo['texto'][:100]}...\n"
            f"Que Deus abençoe seu(ua) {descricao}! ❤️ #Shorts #OraçãoDoDia"
        ),
        "tags": [
            "Shorts", "oração", saudacao.lower(), "oração do dia", "versículo",
            "Canal Oração", "fé", "Deus", "Jesus", "bênção", "oração curta",
        ],
    }


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scripts.detectar_periodo import detectar_periodo

    os.makedirs("output", exist_ok=True)
    info = detectar_periodo()
    resultado = gerar_conteudo(info)

    with open("output/conteudo.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Conteúdo salvo em output/conteudo.json")
    print(f"   Título: {resultado['titulo']}")
