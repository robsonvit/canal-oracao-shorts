"""
sortear_tema.py
───────────────
Sorteia um tema de curiosidade bíblica para o gerador de vídeos.
"""

import os
import random

# Banco de dados de categorias e ganchos
TEMAS = [
    # 1. Curiosidades Históricas e Geográficas
    {"gancho": "O mapa que mudará sua leitura da Bíblia.", "categoria": "Geografia Bíblica Oculta", "termos_video": ["ancient ruins", "old map mystery", "desert landscape", "middle east history", "cinematic desert"]},
    {"gancho": "O achado arqueológico que provou esse versículo.", "categoria": "Arqueologia e Descobertas", "termos_video": ["archaeology dig", "ancient artifacts", "stone ruins", "historical discovery", "ancient scrolls"]},
    {"gancho": "Você não duraria um dia no mundo bíblico.", "categoria": "Costumes da Antiguidade", "termos_video": ["ancient village", "desert life", "old times", "ancient culture", "sandstorm"]},
    {"gancho": "O erro fatal que destruiu este rei bíblico.", "categoria": "Impérios e Reis", "termos_video": ["ancient king", "ruined castle", "fallen empire", "golden crown", "history epic"]},
    
    # 2. Correções e Mitos (Erros de Interpretação)
    {"gancho": "Os estudiosos da Bíblia não te contam isso.", "categoria": "Interpretações Erradas", "termos_video": ["ancient books", "dark library", "secret manuscript", "reading old book", "mystery documents"]},
    {"gancho": "Essa mentira sobre a Bíblia virou verdade.", "categoria": "Desmistificando Erros Antigos", "termos_video": ["mystery", "shadows", "ancient text", "burning candle", "secret"]},
    {"gancho": "Esta palavra grega foi traduzida totalmente errada.", "categoria": "Traduções que Mudam Tudo", "termos_video": ["ancient writing", "greek letters", "old scrolls", "scholar writing", "ancient text"]},
    {"gancho": "Essa frase não significa o que você pensa.", "categoria": "Contexto Cultural", "termos_video": ["ancient people", "history mystery", "middle east", "old scripture", "ancient temple"]},
    
    # 3. Análise de Texto (Exegese e Teologia)
    {"gancho": "O segredo escondido no texto original desse versículo.", "categoria": "Exegese de Passagens", "termos_video": ["secret code", "ancient script", "hidden message", "hebrew letters", "mysterious symbols"]},
    {"gancho": "A verdade teológica que vai incomodar muita gente.", "categoria": "Teologia Sem Filtros", "termos_video": ["storm clouds", "dark sky", "dramatic lighting", "cinematic shadow", "stormy weather"]},
    {"gancho": "Três mistérios bíblicos que ninguém consegue explicar.", "categoria": "Mistérios Ocultos", "termos_video": ["mystery fog", "dark forest", "creepy shadows", "unexplained phenomenon", "mysterious light"]},
    {"gancho": "O código secreto por trás desse número na Bíblia.", "categoria": "Simbolismos Profundos", "termos_video": ["sacred geometry", "ancient numbers", "mysterious symbols", "math mystery", "stars night sky"]},
    
    # 4. Narrativas e Personagens (Passagens e Episódios)
    {"gancho": "A lição mais óbvia da Bíblia que você ignora.", "categoria": "Conclusões Simples de Passagens", "termos_video": ["peaceful nature", "sunlight rays", "reading bible", "calm wisdom", "nature reflection"]},
    {"gancho": "O herói bíblico que a sua igreja esconde.", "categoria": "Personagens Lado B", "termos_video": ["hidden hero", "ancient warrior", "forgotten history", "lone figure desert", "epic cinematic"]},
    {"gancho": "Este foi o ato mais cruel de toda a Bíblia.", "categoria": "Vilões e Tramas", "termos_video": ["fire burning", "dark ruins", "battlefield smoke", "creepy silhouette", "war destruction"]},
    {"gancho": "O capítulo mais bizarro da Bíblia que você pulou.", "categoria": "Histórias Incomuns", "termos_video": ["weird phenomenon", "surreal landscape", "bizarre mystery", "creepy shadow", "alien like"]},
    
    # 5. Profecias, Escatologia e Apocalipse
    {"gancho": "A profecia de 2500 anos que se cumpriu ontem.", "categoria": "Profecias Cumpridas", "termos_video": ["clock ticking", "ancient hourglass", "epic sky", "time passing", "modern vs ancient"]},
    {"gancho": "O real significado da marca da besta revelado.", "categoria": "Símbolos do Apocalipse", "termos_video": ["fire flames", "scary red light", "dark ominous", "apocalypse sky", "mark symbol"]},
    {"gancho": "O próximo evento apocalíptico que a Bíblia prevê.", "categoria": "Eventos Futuros", "termos_video": ["meteor shower", "storm apocalypse", "volcano eruption", "world ending", "dark clouds lightning"]},
    {"gancho": "O livro profético que foi proibido de ser lido.", "categoria": "Livros Selados", "termos_video": ["locked book", "chains", "secret vault", "forbidden scroll", "dark magic book"]},
    
    # 6. Curiosidades Visuais e "Shock Value"
    {"gancho": "A verdadeira aparência dos anjos vai te dar pesadelos.", "categoria": "Anjos Reais", "termos_video": ["many eyes", "biblical angel", "scary wings", "creepy light", "ethereal terrifying"]},
    {"gancho": "O monstro real que a Bíblia descreve em detalhes.", "categoria": "Criaturas Mitológicas/Bíblicas", "termos_video": ["sea monster", "leviathan", "scary beast", "dragon scale", "dark ocean storm"]},
    {"gancho": "A arma bíblica mais letal que a história registrou.", "categoria": "Armas e Guerras", "termos_video": ["ancient sword", "battlefield ancient", "warrior weapon", "epic battle", "fire sparks"]},
    {"gancho": "O ritual de sangue bíblico que você não conhecia.", "categoria": "Rituais Antigos", "termos_video": ["ancient altar", "blood ritual", "dark temple", "sacrificial", "creepy fire"]},
]

def sortear_tema() -> dict:
    """
    Sorteia um gancho e retorna os metadados do vídeo.
    """
    tema_selecionado = random.choice(TEMAS)
    
    # Todos usarão uma key geral de mistério para a música
    tema_selecionado["musica_key"] = "misterio"
    
    print(f"🎬 Tema Sorteado: {tema_selecionado['categoria']}")
    print(f"   Gancho: {tema_selecionado['gancho']}")
    
    return tema_selecionado

if __name__ == "__main__":
    info = sortear_tema()
    print(info)
