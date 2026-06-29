"""
pipeline.py
───────────
Orquestrador principal do Canal Oração Shorts.
Detecta o período do dia e executa todos os passos em sequência:

  1. Detectar período (bom dia / boa tarde / boa noite)
  2. Gerar oração curta + versículo bíblico via Groq AI
  3. Gerar áudio TTS masculino + legendas SRT
  4. Baixar música instrumental por período
  5. Buscar e processar clipes de vídeo portrait (9:16) do Pexels
  6. Montar Short 1080×1920 com card de versículo + legendas destacadas
  7. Upload para o YouTube como Short (publicação imediata)

Uso:
    python scripts/pipeline.py
    PERIODO=boa_noite python scripts/pipeline.py   ← força período
"""

import os
import sys
import json
import traceback

ROOT_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")
sys.path.insert(0, ROOT_DIR)


def _titulo(passo: int, total: int, descricao: str):
    print(f"\n{'─'*60}")
    print(f" PASSO {passo}/{total}: {descricao}")
    print(f"{'─'*60}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(ROOT_DIR, "data"), exist_ok=True)

    print("\n" + "═"*60)
    print("  📱  CANAL ORAÇÃO — SHORTS PIPELINE")
    print("═"*60)

    # ──────────────────────────────────────────────────────────────────────────
    # PASSO 1 — Detectar período do dia
    # ──────────────────────────────────────────────────────────────────────────
    _titulo(1, 7, "Detectando período do dia...")
    from scripts.detectar_periodo import detectar_periodo

    periodo_info = detectar_periodo()
    print(f"✅ {periodo_info['emoji']} {periodo_info['saudacao']} | "
          f"Período: {periodo_info['periodo']}")

    # ──────────────────────────────────────────────────────────────────────────
    # PASSO 2 — Gerar oração curta + versículo via Groq AI
    # ──────────────────────────────────────────────────────────────────────────
    _titulo(2, 7, "Gerando oração e versículo com Groq AI (llama-3.3-70b)...")
    from scripts.gerar_conteudo import gerar_conteudo

    dados = gerar_conteudo(periodo_info)
    conteudo_json = os.path.join(OUTPUT_DIR, "conteudo.json")

    palavras = len(dados["oracao_texto"].split())
    print(f"✅ Versículo : {dados['versiculo_ref']}")
    print(f"   Oração   : {palavras} palavras ({palavras/2.5:.0f}s estimado)")
    print(f"   Título   : {dados['titulo']}")

    with open(conteudo_json, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    # ──────────────────────────────────────────────────────────────────────────
    # PASSO 3 — Gerar áudio TTS e legendas SRT
    # ──────────────────────────────────────────────────────────────────────────
    _titulo(3, 7, "Gerando áudio TTS masculino + legendas (edge-tts + Groq Whisper)...")
    from scripts.gerar_audio import gerar as gerar_audio

    audio_path, srt_path = gerar_audio(dados["oracao_texto"], OUTPUT_DIR)

    # ──────────────────────────────────────────────────────────────────────────
    # PASSO 4 — Baixar música instrumental por período
    # ──────────────────────────────────────────────────────────────────────────
    _titulo(4, 7, f"Baixando música de fundo para '{periodo_info['saudacao']}'...")
    from scripts.baixar_musica import baixar_musica

    musica_path = baixar_musica(periodo_info["periodo"])
    print(f"✅ Música: {musica_path}")

    # ──────────────────────────────────────────────────────────────────────────
    # PASSO 5 — Buscar e processar clipes de vídeo portrait (9:16)
    # ──────────────────────────────────────────────────────────────────────────
    _titulo(5, 7, "Buscando clipes portrait 9:16 (Pexels)...")
    from scripts.buscar_video import buscar_e_processar_clips

    clips = buscar_e_processar_clips(
        termos_busca=periodo_info["termos_video"],
        n_clips=5,
        output_dir=OUTPUT_DIR,
    )
    print(f"✅ {len(clips)} clipes prontos")

    # ──────────────────────────────────────────────────────────────────────────
    # PASSO 6 — Montar Short 1080×1920
    # ──────────────────────────────────────────────────────────────────────────
    _titulo(6, 7, "Montando Short 1080×1920 com card de versículo + legendas...")
    from scripts.montar_video import montar_video

    video_final = montar_video(
        clips           = clips,
        audio_path      = audio_path,
        legendas_srt    = srt_path,
        musica_path     = musica_path,
        output_dir      = OUTPUT_DIR,
        versiculo_texto = dados["versiculo_texto"],
        versiculo_ref   = dados["versiculo_ref"],
    )

    # ──────────────────────────────────────────────────────────────────────────
    # PASSO 7 — Upload para o YouTube como Short
    # ──────────────────────────────────────────────────────────────────────────
    _titulo(7, 7, "Publicando Short no YouTube...")

    if not os.environ.get("YOUTUBE_REFRESH_TOKEN"):
        print("⚠️  YOUTUBE_REFRESH_TOKEN não configurado.")
        print("   Configure os secrets no GitHub e rode novamente.")
        print(f"\n   Short salvo localmente em: {video_final}")
    else:
        from scripts.upload_youtube import upload_youtube
        video_id = upload_youtube(video_final, dados)
        print(f"\n🎉 SHORT PUBLICADO COM SUCESSO!")
        print(f"   📱 https://www.youtube.com/shorts/{video_id}")

    # ── Resumo final ───────────────────────────────────────────────────────
    print("\n" + "═"*60)
    print("  📁 Arquivos gerados:")
    for nome in ["conteudo.json", "audio.mp3", "legendas.srt"]:
        caminho = os.path.join(OUTPUT_DIR, nome)
        if os.path.exists(caminho):
            tamanho = os.path.getsize(caminho)
            print(f"     {nome:<22} {tamanho/1024:.0f} KB")
    for arq in os.listdir(OUTPUT_DIR):
        if arq.endswith(".mp4") and not arq.startswith("clip") and not arq.startswith("nature") and not arq.startswith("card"):
            caminho = os.path.join(OUTPUT_DIR, arq)
            tamanho = os.path.getsize(caminho)
            print(f"     {arq:<22} {tamanho/1024/1024:.1f} MB")
            break
    print("═"*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        traceback.print_exc()
        sys.exit(1)
