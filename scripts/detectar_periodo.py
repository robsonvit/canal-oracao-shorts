"""
detectar_periodo.py
───────────────────
Detecta o período do dia (bom_dia / boa_tarde / boa_noite) com base
no horário atual (UTC-3, fuso de Brasília) e retorna todas as
configurações temáticas associadas.

Períodos:
  06:00 – 11:59  → bom_dia    (nascer do sol)
  12:00 – 17:59  → boa_tarde  (entardecer)
  18:00 – 05:59  → boa_noite  (lua / estrelas)
"""

from datetime import datetime, timezone, timedelta
import os

# Fuso de Brasília = UTC-3
TZ_BRASIL = timezone(timedelta(hours=-3))


# ─────────────────────────────────────────────────────────────────────────────
# Configurações por período
# ─────────────────────────────────────────────────────────────────────────────
PERIODOS = {
    "bom_dia": {
        "saudacao":    "Bom dia",
        "emoji":       "☀️",
        "descricao":   "manhã",
        "termos_video": [
            "sunrise nature beautiful",
            "morning light forest",
            "dawn sky golden",
            "sunrise mountains mist",
            "morning dew grass sunlight",
            "golden hour morning",
            "sunrise ocean waves",
            "peaceful morning nature",
            "birds singing morning",
            "sunrise clouds sky",
        ],
        "musica_key": "bom_dia",
        # Músicas matutinas do Archive.org (domínio público)
        "musicas": [
            "https://archive.org/download/MorningMoodGreig/Morning_Mood_-_Grieg.mp3",
            "https://archive.org/download/ClassicalMusicPlaylist/Pachelbel_Canon_in_D.mp3",
        ],
        "musica_fallback": "https://archive.org/download/BaptistMusic/How%20Beautiful%20-%20piano%20instrumental%20cover%20with%20lyrics.mp3",
    },
    "boa_tarde": {
        "saudacao":    "Boa tarde",
        "emoji":       "🌅",
        "descricao":   "tarde",
        "termos_video": [
            "sunset golden hour nature",
            "afternoon sky clouds",
            "warm sunset light field",
            "sunset ocean beautiful",
            "golden hour meadow sunset",
            "evening light trees",
            "sunset mountains silhouette",
            "warm afternoon nature",
            "sunset clouds colors",
            "peaceful sunset river",
        ],
        "musica_key": "boa_tarde",
        "musicas": [
            "https://archive.org/download/ClassicalMusicPlaylist/Debussy_Clair_de_lune.mp3",
            "https://archive.org/download/BaptistMusic/How%20Beautiful%20-%20piano%20instrumental%20cover%20with%20lyrics.mp3",
        ],
        "musica_fallback": "https://archive.org/download/BaptistMusic/How%20Beautiful%20-%20piano%20instrumental%20cover%20with%20lyrics.mp3",
    },
    "boa_noite": {
        "saudacao":    "Boa noite",
        "emoji":       "🌙",
        "descricao":   "noite",
        "termos_video": [
            "night sky moon stars",
            "moonlight peaceful nature",
            "stars night sky milky way",
            "moon reflection water night",
            "peaceful night forest",
            "night sky clouds moon",
            "starry night beautiful",
            "calm night nature moonlight",
            "moon rising sky",
            "night garden peaceful",
        ],
        "musica_key": "boa_noite",
        "musicas": [
            "https://archive.org/download/ClassicalMusicPlaylist/Beethoven_Moonlight_Sonata.mp3",
            "https://archive.org/download/BaptistMusic/How%20Beautiful%20-%20piano%20instrumental%20cover%20with%20lyrics.mp3",
        ],
        "musica_fallback": "https://archive.org/download/BaptistMusic/How%20Beautiful%20-%20piano%20instrumental%20cover%20with%20lyrics.mp3",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Função principal
# ─────────────────────────────────────────────────────────────────────────────
def detectar_periodo(hora_override: int | None = None) -> dict:
    """
    Detecta o período do dia com base no horário atual (UTC-3).

    Parâmetros:
        hora_override — int (0-23) para forçar um horário (útil em testes).
                        Se None, usa o horário atual do sistema.

    Retorna dict com todas as configurações do período.
    """
    # Permite forçar via variável de ambiente (ex.: PERIODO=boa_noite)
    periodo_env = os.environ.get("PERIODO", "").lower().strip()
    if periodo_env in PERIODOS:
        print(f"⚙️  Período forçado via env: {periodo_env}")
        return {"periodo": periodo_env, **PERIODOS[periodo_env]}

    if hora_override is not None:
        hora = hora_override
    else:
        agora_br = datetime.now(TZ_BRASIL)
        hora = agora_br.hour

    if 6 <= hora < 12:
        periodo = "bom_dia"
    elif 12 <= hora < 18:
        periodo = "boa_tarde"
    else:
        periodo = "boa_noite"

    print(f"🕐 Hora atual (BRT): {hora:02d}h → Período: {periodo}")
    return {"periodo": periodo, **PERIODOS[periodo]}


if __name__ == "__main__":
    info = detectar_periodo()
    print(f"\n{info['emoji']} {info['saudacao']}!")
    print(f"   Período   : {info['periodo']}")
    print(f"   Descrição : {info['descricao']}")
    print(f"   Termos    : {info['termos_video'][:3]}...")
