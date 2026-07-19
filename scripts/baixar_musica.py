"""
baixar_musica.py
────────────────
Baixa músicas instrumentais sem direitos autorais do Archive.org
para estilo de curiosidades bíblicas/mistério.

Cada música é cacheada localmente em data/bg_music_{key}.mp3
para evitar download repetido.
"""

import os
import requests

# ─────────────────────────────────────────────────────────────────────────────
# Músicas por estilo (Archive.org — domínio público / Creative Commons)
# ─────────────────────────────────────────────────────────────────────────────
MUSICAS = {
    # Músicas de suspense, épicas, sombrias
    "misterio": [
        "https://archive.org/download/HolstThePlanetsMars/01MarsTheBringerOfWar.mp3",
        "https://archive.org/download/BachToccataAndFugueInDMinor_201705/Bach-Toccata-and-Fugue-in-d-minor.mp3",
    ]
}

# Fallback garantido (sempre disponível)
FALLBACK_URL = (
    "https://archive.org/download/BeethovenSymphonyNo.5_201705/01-SymphonyNo.5InCMinorOp.67-I.AllegroConBrio.mp3"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def baixar_musica(musica_key: str = "misterio") -> str:
    """
    Garante que a música de fundo para o estilo está disponível localmente.

    Parâmetros:
        musica_key — ex: "misterio"

    Retorna o caminho para o arquivo MP3.
    """
    dest = f"data/bg_music_{musica_key}.mp3"

    if os.path.exists(dest):
        print(f"🎵 Música já existe: {dest}")
        return dest

    os.makedirs("data", exist_ok=True)

    urls = MUSICAS.get(musica_key, []) + [FALLBACK_URL]

    for url in urls:
        print(f"🎵 Baixando música para '{musica_key}': {url[:60]}...")
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

    raise RuntimeError(f"Não foi possível baixar música para a chave '{musica_key}'.")


if __name__ == "__main__":
    for p in ["misterio"]:
        caminho = baixar_musica(p)
        print(f"  {p}: {caminho}")
