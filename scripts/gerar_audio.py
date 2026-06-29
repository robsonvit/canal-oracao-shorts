"""
gerar_audio.py
──────────────
Gera áudio MP3 com voz grave masculina (pt-BR-AntonioNeural) via edge-tts
para o Short (60–90 segundos) e produz um arquivo SRT de legendas
com timestamps via Groq Whisper.

Diferenças em relação ao projeto principal:
  - Rate: -10% (mais ágil que o principal para caber em ~75s)
  - Pitch: -5Hz (levemente grave, mas sem exagero para Short)
  - Palavras por legenda: 4 (tela menor no mobile)
"""

import asyncio
import os
import json

import edge_tts
from groq import Groq


# ─────────────────────────────────────────────────────────────────────────────
# Configurações da voz
# ─────────────────────────────────────────────────────────────────────────────
VOZ = "pt-BR-AntonioNeural"   # Voz masculina natural do Brasil
PALAVRAS_POR_LEGENDA = 4      # Menos palavras por bloco (tela portrait/mobile)


# ─────────────────────────────────────────────────────────────────────────────
# Geração principal (assíncrona)
# ─────────────────────────────────────────────────────────────────────────────
async def _gerar_async(texto: str, output_dir: str) -> tuple[str, str]:
    """Gera MP3 + SRT de forma assíncrona."""
    # Rate -10%: mais rápido que o principal (-20%) para o Short caber em ~75s
    # Pitch -5Hz: levemente grave, mantém naturalidade
    communicate = edge_tts.Communicate(texto, VOZ, rate="-10%", pitch="-5Hz")

    audio_path = os.path.join(output_dir, "audio.mp3")
    srt_path   = os.path.join(output_dir, "legendas.srt")

    with open(audio_path, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])

    def _segundos_para_hms(segundos: float) -> str:
        horas   = int(segundos // 3600)
        minutos = int((segundos % 3600) // 60)
        segs    = int(segundos % 60)
        ms      = int(round((segundos - int(segundos)) * 1000))
        return f"{horas:02d}:{minutos:02d}:{segs:02d},{ms:03d}"

    # Gerar legendas SRT via Groq Whisper
    print("🎙️  Gerando legendas com Groq Whisper...")
    cliente_groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    try:
        with open(audio_path, "rb") as f:
            transcricao = cliente_groq.audio.transcriptions.create(
                file=("audio.mp3", f.read()),
                model="whisper-large-v3-turbo",
                response_format="verbose_json",
                language="pt"
            )

        linhas_srt = []
        segmentos = (
            transcricao.get("segments", [])
            if isinstance(transcricao, dict)
            else transcricao.segments
        )

        idx = 1
        for segment in segmentos:
            try:
                start = segment.start
                end   = segment.end
                text  = segment.text
            except AttributeError:
                start = segment["start"]
                end   = segment["end"]
                text  = segment["text"]

            palavras = text.strip().split()
            if not palavras:
                continue

            chunk_size      = PALAVRAS_POR_LEGENDA
            duracao_total   = end - start
            tempo_por_palavra = duracao_total / len(palavras)

            for i in range(0, len(palavras), chunk_size):
                chunk       = palavras[i: i + chunk_size]
                chunk_text  = " ".join(chunk)
                chunk_start = start + (i * tempo_por_palavra)
                chunk_end   = start + ((i + len(chunk)) * tempo_por_palavra)

                inicio = _segundos_para_hms(chunk_start)
                fim    = _segundos_para_hms(chunk_end)
                linhas_srt.append(f"{idx}\n{inicio} --> {fim}\n{chunk_text}\n")
                idx += 1

        srt_content = "\n".join(linhas_srt)

        if not srt_content.strip():
            raise ValueError("Groq retornou legenda vazia")

    except Exception as e:
        print(f"⚠️ Erro ao transcrever com Groq: {e}. Usando fallback.")
        srt_content = "1\n00:00:00,000 --> 00:00:05,000\n \n"

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    print(f"✅ Áudio gerado : {audio_path}")
    print(f"✅ Legendas SRT : {srt_path}")
    return audio_path, srt_path


# ─────────────────────────────────────────────────────────────────────────────
# Interface pública
# ─────────────────────────────────────────────────────────────────────────────
def gerar(texto: str, output_dir: str = "output") -> tuple[str, str]:
    os.makedirs(output_dir, exist_ok=True)
    return asyncio.run(_gerar_async(texto, output_dir))


if __name__ == "__main__":
    with open("output/conteudo.json", encoding="utf-8") as f:
        data = json.load(f)
    gerar(data["oracao_texto"])
