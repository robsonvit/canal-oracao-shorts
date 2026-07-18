from kokoro import KPipeline
import soundfile as sf
import sys

print("Iniciando pipeline Kokoro...")
try:
    pipeline = KPipeline(lang_code='p')
    print("Pipeline carregado. Gerando audios...")
    text = "A paz do Senhor, irmãos e irmãs!"
    
    # pt-br male voices as seen in docs
    voices = ['pm_alex', 'pm_santa']
    
    for voice in voices:
        print(f"Gerando para voz: {voice}")
        try:
            generator = pipeline(text, voice=voice, speed=1, split_pattern=r'\n+')
            for i, (gs, ps, audio) in enumerate(generator):
                sf.write(f'kokoro_{voice}.wav', audio, 24000)
                print(f"Salvo kokoro_{voice}.wav")
        except Exception as e:
            print(f"Erro com {voice}: {e}")
            
    print("Finalizado!")
except Exception as e:
    print(f"Erro geral: {e}")