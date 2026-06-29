"""
baixar_musica.py
────────────────
Baixa músicas instrumentais sem direitos autorais do Archive.org
por período do dia (bom dia / boa tarde / boa noite).

Cada música é cacheada localmente em data/bg_music_{periodo}.mp3
para evitar download repetido.
"""

import os
import requests

# ─────────────────────────────────────────────────────────────────────────────
# Músicas por período (Archive.org — domínio público / Creative Commons)
# ─────────────────────────────────────────────────────────────────────────────
MUSICAS = {
    # Manhã: Canon de Pachelbel — suave, esperançoso, perfeito para despertar
    "bom_dia": [
        "https://archive.org/download/ClassicalMusicPlaylist/Pachelbel_Canon_in_D.mp3",
        "https://archive.org/download/BaptistMusic/How%20Beautiful%20-%20piano%20instrumental%20cover%20with%20lyrics.mp3",
    ],

    # Tarde: Gymnopédie de Satie — tranquilo, contemplativo, paz interior
    "boa_tarde": [
        "https://archive.org/download/ClassicalMusicPlaylist/Debussy_Clair_de_lune.mp3",
        "https://archive.org/download/BaptistMusic/How%20Beautiful%20-%20piano%20instrumental%20cover%20with%20lyrics.mp3",
    ],

    # Noite: Moonlight Sonata de Beethoven — noturno, profundo, tranquilizador
    "boa_noite": [
        "https://archive.org/download/ClassicalMusicPlaylist/Beethoven_Moonlight_Sonata.mp3",
        "https://archive.org/download/BaptistMusic/How%20Beautiful%20-%20piano%20instrumental%20cover%20with%20lyrics.mp3",
    ],
}

# Fallback garantido (sempre disponível)
FALLBACK_URL = (
    "https://archive.org/download/BaptistMusic/"
    "How%20Beautiful%20-%20piano%20instrumental%20cover%20with%20lyrics.mp3"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def baixar_musica(periodo: str = "bom_dia") -> str:
    """
    Garante que a música de fundo para o período está disponível localmente.

    Parâmetros:
        periodo — "bom_dia", "boa_tarde" ou "boa_noite"

    Retorna o caminho para o arquivo MP3.
    """
    dest = f"data/bg_music_{periodo}.mp3"

    if os.path.exists(dest):
        print(f"🎵 Música já existe: {dest}")
        return dest

    os.makedirs("data", exist_ok=True)

    urls = MUSICAS.get(periodo, []) + [FALLBACK_URL]

    for url in urls:
        print(f"🎵 Baixando música para '{periodo}': {url[:60]}...")
        try:
            r = requests.get(url, headers=HEADERS, stream=True, timeout=45)
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Música salva: {dest}")
            return dest
        except Exception as e:
            print(f"⚠️  Falha ao baixar '{url[:60]}': {e}")
            if os.path.exists(dest):
                os.remove(dest)
            continue

    raise RuntimeError(f"Não foi possível baixar música para o período '{periodo}'.")


if __name__ == "__main__":
    for p in ["bom_dia", "boa_tarde", "boa_noite"]:
        caminho = baixar_musica(p)
        print(f"  {p}: {caminho}")
