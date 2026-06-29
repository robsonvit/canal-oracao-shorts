"""
montar_video.py
───────────────
Monta o vídeo final 1080×1920 (9:16 portrait) para YouTube Shorts a partir de:
  • Lista de clipes já processados (portrait + hflip + 0.85x)
  • Áudio TTS masculino em MP3
  • Legendas SRT centralizadas com sombra e fundo semitransparente
  • Música de fundo instrumental
  • Card inicial com versículo bíblico estilizado (primeiros 5s)

Resolução final: 1080×1920 (portrait — padrão YouTube Shorts)
"""

import os
import json
import subprocess
import re
import random


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _duracao_audio(audio_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        audio_path,
    ]
    resultado = subprocess.run(cmd, capture_output=True, text=True)
    try:
        dados = json.loads(resultado.stdout)
        return float(dados["format"]["duration"])
    except Exception:
        raise RuntimeError(f"Não foi possível obter duração de: {audio_path}")


def _criar_concat_list(clips: list[str], lista_path: str, duracao_alvo: float, duracao_clip: float = 5.88):
    """Cria lista de concatenação longa repetindo clipes sem sequência igual."""
    n_total = int(duracao_alvo / duracao_clip) + 3

    lista_final = []
    ultimo_clipe = None

    for _ in range(n_total):
        opcoes   = [c for c in clips if c != ultimo_clipe] if len(clips) > 1 else clips
        escolhido = random.choice(opcoes)
        lista_final.append(escolhido)
        ultimo_clipe = escolhido

    with open(lista_path, "w", encoding="utf-8") as f:
        for clip in lista_final:
            caminho = os.path.abspath(clip).replace("\\", "/")
            f.write(f"file '{caminho}'\n")


def _escape_srt_path(path: str) -> str:
    path = path.replace("\\", "/")
    path = re.sub(r"^([A-Za-z]):", r"\1\\:", path)
    return path


def _criar_card_versiculo(versiculo_texto: str, versiculo_ref: str, output_dir: str) -> str:
    """
    Cria um clipe de 5 segundos com o versículo em texto sobre fundo preto
    semitransparente usando FFmpeg drawtext.

    Retorna o caminho do clipe gerado.
    """
    card_path = os.path.join(output_dir, "card_versiculo.mp4")

    # Quebra o versículo em linhas de ~35 chars para caber na tela 1080px
    palavras = versiculo_texto.split()
    linhas = []
    linha_atual = []
    chars = 0
    for p in palavras:
        if chars + len(p) + 1 > 32:
            linhas.append(" ".join(linha_atual))
            linha_atual = [p]
            chars = len(p)
        else:
            linha_atual.append(p)
            chars += len(p) + 1
    if linha_atual:
        linhas.append(" ".join(linha_atual))

    texto_formatado = r"\n".join(linhas)
    ref_formatada   = f"— {versiculo_ref}"

    # Escapa aspas e caracteres especiais para FFmpeg drawtext
    def _esc(s: str) -> str:
        return s.replace("'", "\\'").replace(":", r"\:").replace(",", r"\,")

    texto_esc = _esc(texto_formatado)
    ref_esc   = _esc(ref_formatada)

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "color=c=black:size=1080x1920:rate=30:duration=5",
        "-vf", (
            # Fundo semitransparente (retângulo escuro)
            "drawbox=x=40:y=600:w=1000:h=680:color=black@0.70:t=fill,"
            # Texto do versículo
            f"drawtext=fontsize=52:fontcolor=white:x=80:y=640:"
            f"text='{texto_esc}':"
            f"line_spacing=18:shadowcolor=black:shadowx=2:shadowy=2,"
            # Referência do versículo
            f"drawtext=fontsize=42:fontcolor=#FFD700:x=80:y=(h-300):"
            f"text='{ref_esc}':"
            f"shadowcolor=black:shadowx=2:shadowy=2"
        ),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-an",
        card_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"⚠️  Falha ao criar card do versículo: {result.stderr[-300:]}")
        return None

    print(f"✅ Card do versículo criado: {card_path}")
    return card_path


# ─────────────────────────────────────────────────────────────────────────────
# Função principal
# ─────────────────────────────────────────────────────────────────────────────
def montar_video(
    clips: list[str],
    audio_path: str,
    legendas_srt: str,
    musica_path: str,
    output_dir: str = "output",
    versiculo_texto: str = "",
    versiculo_ref: str = "",
) -> str:
    """
    Monta o Short final 1080×1920 e retorna o caminho do vídeo gerado.

    clips           → clipes MP4 portrait já processados
    audio_path      → MP3 gerado pelo TTS
    legendas_srt    → arquivo SRT com timestamps
    musica_path     → MP3 da música de fundo
    output_dir      → pasta de saída
    versiculo_texto → texto do versículo para o card inicial
    versiculo_ref   → referência bíblica (ex: "Salmos 4:8")
    """
    os.makedirs(output_dir, exist_ok=True)

    duracao_audio = _duracao_audio(audio_path)
    print(f"⏱️  Duração do áudio : {duracao_audio:.1f}s ({duracao_audio/60:.1f} min)")
    print(f"🎬 Clipes disponíveis: {len(clips)}")

    # ── Passo 1: Card do versículo (5s inicial) ───────────────────────────────
    card_path = None
    if versiculo_texto:
        print("📖 Criando card do versículo...")
        card_path = _criar_card_versiculo(versiculo_texto, versiculo_ref, output_dir)

    # ── Passo 2: Lista de concatenação de clipes de natureza ──────────────────
    lista_concat = os.path.join(output_dir, "concat_list.txt")
    _criar_concat_list(clips, lista_concat, duracao_audio)

    # ── Passo 3: Concatenar natureza com card do versículo ────────────────────
    output_path  = os.path.join(output_dir, "video_final.mp4")
    srt_escaped  = _escape_srt_path(legendas_srt)

    # Estilo de legenda para Short:
    # - FontSize 55 (maior, pois tela é portrait/mobile)
    # - Sombra tripla + fundo semitransparente para máxima legibilidade
    subtitle_style = ",".join([
        "Fontname=Arial",
        "FontSize=55",
        "PrimaryColour=&H00FFFFFF",    # Branco
        "OutlineColour=&H00000000",    # Contorno preto
        "BackColour=&H99000000",       # Fundo preto 60% opaco
        "BorderStyle=4",               # Box (retângulo de fundo)
        "Outline=2",
        "Shadow=3",
        "Alignment=10",                # Centro da tela
        "MarginV=180",                 # Afasta da base para não sobrepor elementos
    ])

    print(f"🎞️  Montando Short final 1080×1920 (duração alvo: {duracao_audio:.0f}s)...")

    if card_path and os.path.exists(card_path):
        # Com card de versículo: concat(card + natureza) → legendas → mix áudio
        card_list = os.path.join(output_dir, "card_list.txt")
        with open(card_list, "w", encoding="utf-8") as f:
            card_abs = os.path.abspath(card_path).replace("\\", "/")
            f.write(f"file '{card_abs}'\n")

        # Primeiro combina card + natureza loopada
        nature_base = os.path.join(output_dir, "nature_base.mp4")
        cmd_base = [
            "ffmpeg", "-y",
            "-i", card_path,
            "-f", "concat", "-safe", "0", "-i", lista_concat,
            "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]",
            "-map", "[v]",
            "-t", str(duracao_audio),
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-pix_fmt", "yuv420p", "-an",
            nature_base,
        ]
        res_base = subprocess.run(cmd_base, capture_output=True, text=True)
        if res_base.returncode != 0:
            print(f"⚠️  Falha ao criar base com card: {res_base.stderr[-300:]}")
            base_input = ["-f", "concat", "-safe", "0", "-i", lista_concat]
        else:
            base_input = ["-i", nature_base]
    else:
        base_input = ["-f", "concat", "-safe", "0", "-i", lista_concat]

    cmd_final = [
        "ffmpeg", "-y",
        *base_input,
        "-i", audio_path,
        "-stream_loop", "-1", "-i", musica_path,
        "-t", str(duracao_audio),
        "-map", "[v]",
        "-map", "[a]",
        "-filter_complex", (
            f"[0:v]eq=brightness=-0.03:contrast=1.02,"
            f"subtitles='{srt_escaped}':force_style='{subtitle_style}'[v];"
            "[1:a]volume=1.0[voice];"
            "[2:a]volume=0.15[bg];"
            "[voice][bg]amix=inputs=2:duration=first:dropout_transition=2[a]"
        ),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "24",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        "-map_metadata", "-1",
        output_path,
    ]

    resultado = subprocess.run(cmd_final, capture_output=True, text=True)
    if resultado.returncode != 0:
        raise RuntimeError(f"FFmpeg falhou na montagem final:\n{resultado.stderr[-600:]}")

    tamanho_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"✅ Short final pronto: {output_path}  ({tamanho_mb:.1f} MB)")
    return output_path


if __name__ == "__main__":
    import glob
    clips = sorted(glob.glob("output/clips/clip_*.mp4"))
    montar_video(
        clips,
        "output/audio.mp3",
        "output/legendas.srt",
        "data/bg_music_bom_dia.mp3",
        versiculo_texto="Em paz me deito e logo adormeço, pois só tu, Senhor, me fazes repousar em segurança.",
        versiculo_ref="Salmos 4:8",
    )
