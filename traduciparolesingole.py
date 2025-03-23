import re
import time
from deep_translator import GoogleTranslator
from deep_translator.exceptions import TranslationNotFound
from spellchecker import SpellChecker

# Lista di parole riservate che non devono essere tradotte (parole di programmazione, funzioni, etc.)
reserved_words = {
    "function", "if", "else", "while", "return", "class", "for", "switch", "case", "try", "catch", "finally", 
    "continue", "break", "new", "const", "let", "var", "this", "prototype", "arguments", "argument0", "argument1",
    "sprite_get_height", "sprite_get_width", "obj_enemy", "obj_creature", "obj_arena", "obj_treasuregolem", 
    "obj_battlecontroller", "diffused", "tasks", "tid", "strategy", "real", "__prop", "__slot", 
    # Aggiungere qui altre parole riservate a seconda delle necessità
}

def should_translate(word, spell_checker):
    # Ignora se contiene spazio, underscore, più di una lettera maiuscola, simboli o numeri
    if (" " in word or "_" in word or len(re.findall(r"[A-Z]", word)) > 1 or
        re.search(r"[^a-zA-Z]", word)):
        return False
    # Verifica se la parola è nel dizionario inglese
    if word.lower() not in spell_checker:
        print(f"Parola non trovata nel dizionario: {word}")
        return False
    # Verifica se la parola è una parola riservata di programmazione
    if word.lower() in reserved_words:
        print(f"Parola riservata (probabile codice): {word}")
        return False
    return True

def translate_file(input_file, output_file):
    translator = GoogleTranslator(source='en', target='it')
    spell_checker = SpellChecker()
    translations_count = 0
    line_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            line_count += 1
            match = re.search(r'"(.*?)"', line)
            if match:
                word = match.group(1)
                if should_translate(word, spell_checker):
                    try:
                        translated_word = translator.translate(word)
                        line = line.replace(f'"{word}"', f'"{translated_word}"')
                        translations_count += 1
                    except TranslationNotFound:
                        print(f"Impossibile tradurre: {word}")
            
            outfile.write(line)
            
            # Output ogni 500 righe
            if line_count % 500 == 0:
                print(f"Righe processate: {line_count}, Traduzioni effettuate: {translations_count}")
                time.sleep(2)  # Pausa per evitare il blocco API
    
    print(f"Traduzione completata. Totale righe: {line_count}, Traduzioni effettuate: {translations_count}")

# Esempio di utilizzo
translate_file("strings_translated.txt", "strings_translated_output.txt")
