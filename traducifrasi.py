import re
import time
import google.generativeai as genai

# CONFIGURAZIONE GEMINI API (INSERIRE LA CHIAVE API)
genai.configure(api_key="xxxxxxxxxxxxxxxxxxxxxx")  # Sostituire con la chiave API reale

# File di input e output
input_file = "strings.txt"
output_file = "strings_translated.txt"

# Contatori
total_lines = sum(1 for _ in open(input_file, "r", encoding="utf-8"))
translated_count = 0
processed_count = 0

print(f"📂 File caricato: {input_file} ({total_lines} righe totali)")
print("🔄 Avvio traduzione con Google Gemini...\n")

# Parole RPG da tradurre sempre (tranne se la riga contiene "_")
rpg_terms = {

}

# Crea il modello Gemini
model = genai.GenerativeModel("gemini-2.0-flash")

# Funzione per tradurre con Google Gemini con output pulito
def gemini_translate(text, max_retries=3):
    prompt = f'Traduci il seguente testo in italiano, riformula (se necessario) per migliorare la sintassi. Restituisci SOLO la traduzione, senza spiegazioni, testo aggiuntivo o informazioni inventate non presenti nel testo inglese: \n"{text}"'

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            translated_text = response.text.strip()

            if translated_text:
                return translated_text
        except Exception as e:
            print(f"⚠️ Errore con Google Gemini: {e} - Tentativo {attempt + 1} di {max_retries}")
            time.sleep(5)  # Aspetta 5 secondi prima di riprovare

    return text  # Restituisce il testo originale se la traduzione fallisce

# Funzione per tradurre solo il testo tra virgolette
def translate_text_in_quotes(line):
    global translated_count, processed_count

    processed_count += 1  # Aumenta il contatore delle righe processate

    # Se la riga contiene "_" (nomi di variabili, codice), viene ignorata completamente
    if "_" in line:
        return line

    # Trova tutto il testo tra virgolette
    matches = re.findall(r'(".*?")', line)
    translated_line = line

    for match in matches:
        text_inside_quotes = match[1:-1]  # Rimuove le virgolette esterne

        # **Convertire \r\n in un vero carattere di nuova riga prima della traduzione**
        temp_text = text_inside_quotes.replace("\\r\\n", "\n")

        # Tradurre se contiene almeno uno spazio o se è un termine RPG noto
        if " " in temp_text or temp_text.lower() in rpg_terms:
            translated_text = rpg_terms.get(temp_text.lower(), gemini_translate(temp_text))

            # **Sostituire virgolette interne con apostrofi solo dopo la traduzione**
            translated_text = translated_text.replace('"', "'")

            # **Ripristinare \r\n dopo la traduzione**
            translated_text = translated_text.replace("\n", "\\r\\n")

            translated_line = translated_line.replace(match, f'"{translated_text}"')
            translated_count += 1

    return translated_line

# Leggere e tradurre riga per riga
with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
    for i, line in enumerate(infile, start=1):
        translated_line = translate_text_in_quotes(line)
        outfile.write(translated_line)

        # Ogni 500 righe, stampa un aggiornamento sullo stato
        if i % 500 == 0:
            completion = (processed_count / total_lines) * 100
            print(f"📌 {processed_count}/{total_lines} righe processate ({completion:.2f}%) - Tradotte: {translated_count}")

        # Ogni 1000 righe, fare una pausa di 2 secondi per evitare blocchi API
        if i % 1000 == 0:
            time.sleep(2)

print("\n✅ Traduzione completata con Google Gemini!")
print(f"📄 Righe tradotte: {translated_count}")
print(f"💾 File salvato: {output_file}")
