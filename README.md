# 📱 Canal Oração — Shorts Automáticos

Automação para geração de YouTube Shorts de oração cristã com versículo bíblico, adaptados ao período do dia.

## 🕐 Funcionamento

| Horário (BRT) | Período | Tema do Vídeo |
|---|---|---|
| 06:00 | ☀️ Bom Dia | Nascer do sol, manhã |
| 12:00 | 🌅 Boa Tarde | Entardecer, tarde |
| 18:00 | 🌙 Boa Noite | Lua, estrelas, noite |

## 🎬 O que é gerado em cada Short

1. **Card inicial (5s)** — Versículo bíblico estilizado com fundo escuro
2. **Vídeo de natureza** — Clipes 9:16 do Pexels temáticos pelo período
3. **Narração TTS** — Voz masculina (`pt-BR-AntonioNeural`) via edge-tts
4. **Oração curta** — 180–220 palavras geradas via Groq AI (llama-3.3-70b)
5. **Versículo aleatório** — Banco de 50 versículos por período
6. **Música de fundo** — Clássica instrumental sem direitos (Archive.org)
7. **Legendas** — Com sombra e fundo semitransparente para máxima legibilidade

## ⚙️ Tecnologias

- **IA**: Groq (`llama-3.3-70b-versatile`) para geração de oração e versículo
- **TTS**: `edge-tts` → `pt-BR-AntonioNeural` (voz masculina)
- **Legendas**: Groq Whisper (`whisper-large-v3-turbo`)
- **Vídeos**: Pexels API (portrait 9:16)
- **Edição**: FFmpeg (legendas, cards, mix de áudio)
- **Upload**: YouTube Data API v3 (publicação imediata)

## 🔑 Secrets necessários

Configure no GitHub → Settings → Secrets → Actions:

```
GROQ_API_KEY           ← API do Groq (mesma do canal principal)
PEXELS_API_KEY         ← API do Pexels (mesma do canal principal)
YOUTUBE_CLIENT_ID      ← OAuth do mesmo canal YouTube
YOUTUBE_CLIENT_SECRET  ← OAuth do mesmo canal YouTube
YOUTUBE_REFRESH_TOKEN  ← Token do mesmo canal YouTube
```

## 🚀 Execução manual

1. Vá em **Actions** → **📱 Gerar Short de Oração**
2. Clique em **Run workflow**
3. Escolha o período (ou deixe vazio para detectar automaticamente)

## 📁 Estrutura

```
scripts/
├── detectar_periodo.py   ← Detecta bom dia/boa tarde/boa noite
├── gerar_conteudo.py     ← Oração + versículo via Groq AI
├── gerar_audio.py        ← TTS + legendas SRT
├── buscar_video.py       ← Clipes portrait do Pexels
├── baixar_musica.py      ← Música instrumental por período
├── montar_video.py       ← FFmpeg: 1080×1920 + legendas + mix
├── upload_youtube.py     ← Upload imediato como Short
└── pipeline.py           ← Orquestrador principal
```

## 🔗 Repositório irmão

Este projeto é complementar ao [canal-oracao](https://github.com/robsonvit/canal-oracao), que gera vídeos longos de oração (15–30 min) para o mesmo canal no YouTube.
