"""
montar_video.py
───────────────
Monta o vídeo final 1080×1920 (9:16 portrait) para YouTube Shorts.
Overlay do card de versículo é feito via filtros (drawbox, drawtext) nos primeiros 6s.
"""

import os
import json
import subprocess
import re
import random


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


def montar_video(
    clips: list[str],
    audio_path: str,
    legendas_srt: str,
    musica_path: str,
    output_dir: str = "output",
    versiculo_texto: str = "",
    versiculo_ref: str = "",
) -> str:
    os.makedirs(output_dir, exist_ok=True)

    duracao_audio = _duracao_audio(audio_path)
    print(f"⏱️  Duração do áudio : {duracao_audio:.1f}s")

    lista_concat = os.path.join(output_dir, "concat_list.txt")
    _criar_concat_list(clips, lista_concat, duracao_audio)

    output_path  = os.path.join(output_dir, "video_final.mp4")
    srt_escaped  = _escape_srt_path(legendas_srt)

    # Fonte reduzida para 18 pois o FFmpeg usa scale relativo ao default 384x288
    # 18 equivale a uma fonte agradável em 1080x1920
    subtitle_style = ",".join([
        "Fontname=Arial",
        "FontSize=18",
        "PrimaryColour=&H00FFFFFF",
        "OutlineColour=&H00000000",
        "BackColour=&H00000000",
        "BorderStyle=1",
        "Outline=2",
        "Shadow=3",
        "Alignment=10",
        "MarginV=90",
    ])

    # Monta a string de filtros de vídeo (sem texto de versículo na tela)
    v_filters = f"[0:v]eq=brightness=-0.03:contrast=1.02,subtitles='{srt_escaped}':force_style='{subtitle_style}'[v]"

    cmd_final = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", lista_concat,
        "-i", audio_path,
        "-stream_loop", "-1", "-i", musica_path,
        "-t", str(duracao_audio),
        "-filter_complex", f"{v_filters};[1:a]volume=1.0[voice];[2:a]volume=0.15[bg];[voice][bg]amix=inputs=2:duration=first:dropout_transition=2[a]",
        "-map", "[v]",
        "-map", "[a]",
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
        raise RuntimeError(f"FFmpeg falhou na montagem final:\n{resultado.stderr[-1000:]}")

    tamanho_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"✅ Short final pronto: {output_path}  ({tamanho_mb:.1f} MB)")
    return output_path
