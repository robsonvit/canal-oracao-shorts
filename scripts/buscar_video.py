"""
buscar_video.py
───────────────
Busca e baixa múltiplos clipes de vídeo do Pexels em formato PORTRAIT (9:16)
para usar como fundo do Short.

Diferenças em relação ao projeto principal:
  ✅ Busca orientação PORTRAIT (9:16) no Pexels
  ✅ Termos de busca dinâmicos por período (bom dia/boa tarde/boa noite)
  ✅ Chaves de tracking separadas por período para não conflitar
  ✅ 5 clipes (vs 12 do principal) — Short é ~75s, clips dão ~30s, loopado
  ✅ Clipes escalados para 1080×1920
"""

import os
import json
import random
import subprocess
import requests
from datetime import datetime, timedelta, timezone

# ─────────────────────────────────────────────────────────────────────────────
# Configurações
# ─────────────────────────────────────────────────────────────────────────────
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
DATA_DIR       = "data"
TRACKING_FILE  = os.path.join(DATA_DIR, "videos_usados_shorts.json")
DIAS_BLOQUEIO  = 5       # Dias mínimos antes de reusar um vídeo
DURACAO_CLIP_S = 5       # Segundos de filmagem original por clipe
VELOCIDADE     = 0.85    # Fator de velocidade (0.85x = levemente mais lento)
NUM_CLIPS      = 5       # Quantidade de clipes distintos a baixar
CLIP_DIR       = os.path.join("output", "clips")


# ─────────────────────────────────────────────────────────────────────────────
# Tracking: controle de vídeos usados recentemente
# ─────────────────────────────────────────────────────────────────────────────
def _carregar_tracking() -> dict:
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _salvar_tracking(tracking: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(TRACKING_FILE, "w", encoding="utf-8") as f:
        json.dump(tracking, f, indent=2, ensure_ascii=False)


def _video_disponivel(video_id: str, tracking: dict) -> bool:
    if str(video_id) not in tracking:
        return True
    ultimo_uso = datetime.fromisoformat(tracking[str(video_id)])
    limite     = datetime.now(timezone.utc) - timedelta(days=DIAS_BLOQUEIO)
    return ultimo_uso < limite


def _marcar_usado(video_id: str, tracking: dict):
    tracking[str(video_id)] = datetime.now(timezone.utc).isoformat()


# ─────────────────────────────────────────────────────────────────────────────
# Busca no Pexels (portrait / vertical)
# ─────────────────────────────────────────────────────────────────────────────
def _buscar_videos_pexels(termo: str, excluir_ids: set, max_resultados: int = 15) -> list:
    """
    Busca vídeos portrait (vertical/9:16) no Pexels.
    Tenta primeiro 'portrait', depois 'vertical' como fallback.
    """
    headers = {"Authorization": PEXELS_API_KEY}

    for orientacao in ["portrait", "landscape"]:
        params = {
            "query":       termo,
            "orientation": orientacao,
            "size":        "medium",
            "per_page":    max_resultados,
        }
        try:
            resp = requests.get(
                "https://api.pexels.com/videos/search",
                headers=headers, params=params, timeout=30
            )
            resp.raise_for_status()
            videos = resp.json().get("videos", [])

            candidatos = []
            for v in videos:
                if v["id"] in excluir_ids:
                    continue

                # Prefere arquivos MP4 em resolução adequada para 9:16
                arquivos_mp4 = [
                    f for f in v.get("video_files", [])
                    if f.get("file_type") == "video/mp4"
                    and f.get("width", 0) >= 720
                ]
                if not arquivos_mp4:
                    arquivos_mp4 = [
                        f for f in v.get("video_files", [])
                        if f.get("file_type") == "video/mp4"
                    ]
                if arquivos_mp4:
                    melhor = max(arquivos_mp4, key=lambda x: x.get("width", 0))
                    candidatos.append({
                        "id":      v["id"],
                        "duracao": v.get("duration", 10),
                        "url":     melhor["link"],
                        "largura": melhor.get("width", 0),
                        "altura":  melhor.get("height", 0),
                    })

            if candidatos:
                return candidatos
        except Exception as e:
            print(f"  ⚠️  Erro na busca '{termo}' ({orientacao}): {e}")

    return []


# ─────────────────────────────────────────────────────────────────────────────
# Download + transformações FFmpeg (9:16 portrait)
# ─────────────────────────────────────────────────────────────────────────────
def _baixar_video(url: str, destino_tmp: str):
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(destino_tmp, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def _processar_clip(input_path: str, output_path: str, duracao_video: int):
    """
    Aplica transformações via FFmpeg para formato 9:16 (1080×1920):
      1. Escolhe posição aleatória de início
      2. Corta 5 segundos
      3. Escala e cropa para 1080×1920 (portrait)
      4. Inverte horizontalmente (hflip) para originalidade
      5. Reduz velocidade para 0.85x
      6. Remove metadados
    """
    velocidade_pts = 1.0 / VELOCIDADE  # 1/0.85 ≈ 1.176
    margem  = max(1, duracao_video - DURACAO_CLIP_S - 1)
    inicio  = random.uniform(0, margem) if margem > 0 else 0

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(inicio),
        "-t",  str(DURACAO_CLIP_S),
        "-i",  input_path,
        "-vf", (
            # Escala para cobrir 1080×1920 mantendo proporção e cropa o excesso
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,"
            "hflip,"
            "fps=30,"
            f"setpts={velocidade_pts:.4f}*PTS"
        ),
        "-an",
        "-map_metadata", "-1",
        "-c:v",    "libx264",
        "-preset", "fast",
        "-crf",    "23",
        "-pix_fmt", "yuv420p",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg erro ao processar clipe:\n{result.stderr[-400:]}")


# ─────────────────────────────────────────────────────────────────────────────
# Interface pública
# ─────────────────────────────────────────────────────────────────────────────
def buscar_e_processar_clips(
    termos_busca: list[str],
    n_clips: int = NUM_CLIPS,
    output_dir: str = "output",
) -> list[str]:
    """
    Busca N vídeos portrait do Pexels com os termos fornecidos (por período),
    processa cada um e retorna lista de caminhos dos clipes prontos.
    """
    os.makedirs(CLIP_DIR, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "tmp_raw"), exist_ok=True)

    tracking = _carregar_tracking()

    bloqueados = {
        vid_id for vid_id, data_uso in tracking.items()
        if not _video_disponivel(vid_id, tracking)
    }

    print(f"📋 Vídeos bloqueados (últimos {DIAS_BLOQUEIO} dias): {len(bloqueados)}")

    termos = termos_busca.copy()
    random.shuffle(termos)

    candidatos_todos: list[dict] = []
    ids_ja_selecionados: set     = set()

    for termo in termos:
        if len(candidatos_todos) >= n_clips * 3:
            break
        novos = _buscar_videos_pexels(
            termo,
            excluir_ids=bloqueados | ids_ja_selecionados
        )
        for c in novos:
            if c["id"] not in ids_ja_selecionados and c["id"] not in bloqueados:
                candidatos_todos.append(c)
                ids_ja_selecionados.add(c["id"])

    if not candidatos_todos:
        print("⚠️  Pool esgotado! Removendo restrição de 5 dias temporariamente...")
        tracking = {}
        for termo in termos[:5]:
            novos = _buscar_videos_pexels(termo, excluir_ids=set(), max_resultados=15)
            candidatos_todos.extend(novos)
        if not candidatos_todos:
            raise RuntimeError("Não foi possível encontrar vídeos no Pexels.")

    random.shuffle(candidatos_todos)
    selecionados = candidatos_todos[:n_clips]

    clips_prontos: list[str] = []

    for i, video in enumerate(selecionados, 1):
        vid_id  = video["id"]
        url     = video["url"]
        duracao = video.get("duracao", 10)

        print(f"  [{i:02d}/{n_clips}] Processando vídeo #{vid_id} "
              f"({video['largura']}x{video['altura']})...")

        tmp_raw  = os.path.join(output_dir, "tmp_raw", f"raw_{vid_id}.mp4")
        clip_out = os.path.join(CLIP_DIR, f"clip_{i:02d}.mp4")

        try:
            _baixar_video(url, tmp_raw)
            _processar_clip(tmp_raw, clip_out, duracao)
            _marcar_usado(str(vid_id), tracking)
            clips_prontos.append(clip_out)

            if os.path.exists(tmp_raw):
                os.remove(tmp_raw)

        except Exception as e:
            print(f"    ⚠️  Falha ao processar vídeo #{vid_id}: {e}")
            if os.path.exists(tmp_raw):
                os.remove(tmp_raw)
            continue

    _salvar_tracking(tracking)

    if not clips_prontos:
        raise RuntimeError("Nenhum clipe foi processado com sucesso.")

    print(f"\n✅ {len(clips_prontos)} clipes prontos em: {CLIP_DIR}/")
    return clips_prontos


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scripts.detectar_periodo import detectar_periodo

    info = detectar_periodo()
    clips = buscar_e_processar_clips(info["termos_video"])
    for c in clips:
        print(f"  • {c}")
