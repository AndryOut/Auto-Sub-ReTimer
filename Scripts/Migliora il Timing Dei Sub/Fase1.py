import os
import pysrt
from tkinter import filedialog

# Funzione per caricare i file
def load_file():
    file_path = filedialog.askopenfilename(title="Seleziona un file")
    if not file_path:
        print("Nessun file selezionato. Chiudendo lo script.")
        exit()
    return file_path

# Funzione per leggere un file .ass
def read_ass_file(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        return file.readlines()

# Filtra i dialoghi in base a `{\\an8}`, inclusi altri tag
def filter_dialogue_by_alignment(dialogue):
    filtered_dialogue = []
    discarded_dialogue = []

    for line in dialogue:
        if '\\an8' in line:  # Cerca "{\an8}" ovunque all'interno della riga, indipendentemente dai tag
            filtered_dialogue.append(line)
        else:
            discarded_dialogue.append(line)

    return filtered_dialogue, discarded_dialogue

# Scrive un file .ass
def write_ass_file(header, dialogue, format_line, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(header + [format_line] + dialogue)

# Scrive un file .srt con gestione precisa dei tempi
def write_srt_file_from_ass(discarded_dialogue, file_path):
    from pysrt import SubRipFile, SubRipTime
    subs = SubRipFile()

    for idx, line in enumerate(discarded_dialogue):
        parts = line.split(',')

        # Calcolo dei tempi di inizio
        start_time_parts = parts[1].strip().split(':')
        start_hours = int(start_time_parts[0])
        start_minutes = int(start_time_parts[1])
        start_seconds = float(start_time_parts[2])
        start_time = SubRipTime(
            start_hours,
            start_minutes,
            int(start_seconds),
            int((start_seconds - int(start_seconds)) * 1000)
        )

        # Calcolo dei tempi di fine
        end_time_parts = parts[2].strip().split(':')
        end_hours = int(end_time_parts[0])
        end_minutes = int(end_time_parts[1])
        end_seconds = float(end_time_parts[2])
        end_time = SubRipTime(
            end_hours,
            end_minutes,
            int(end_seconds),
            int((end_seconds - int(end_seconds)) * 1000)
        )

        # Testo
        text = ','.join(parts[9:]).strip()

        # Crea il sottotitolo
        sub = pysrt.SubRipItem(index=idx + 1, start=start_time, end=end_time, text=text)
        subs.append(sub)

    # Salvataggio file .srt
    subs.save(file_path, encoding='utf-8')

# Processa un file .srt
def process_srt_file(file_path, output_dir):
    subs = pysrt.open(file_path, encoding='utf-8')
    filtered_subs = pysrt.SubRipFile()
    discarded_subs = pysrt.SubRipFile()

    for sub in subs:
        if '\\an8' in sub.text:  # Filtra i sottotitoli con "{\an8}"
            filtered_subs.append(sub)
        else:
            discarded_subs.append(sub)

    filtered_output = os.path.join(output_dir, 'On Top.srt')
    discarded_output = os.path.join(output_dir, 'Sub.srt')

    filtered_subs.save(filtered_output, encoding='utf-8')
    discarded_subs.save(discarded_output, encoding='utf-8')

    print("Sottotitoli processati:")
    print(f"- Righe con \"an8\" salvate in {filtered_output}")
    print(f"- Altre righe salvate in {discarded_output}")

# Individua gli stili di dialogo allineati in alto
def find_top_alignments(styles, dialogue):
    top_alignments = ['7', '8', '9']
    top_styles = []
    alignment_index = None
    for line in styles:
        if line.startswith('Format:'):
            format_parts = [x.strip() for x in line.split(':')[1].split(',')]
            if 'Alignment' in format_parts:
                alignment_index = format_parts.index('Alignment')
        elif line.startswith('Style:') and alignment_index is not None:
            style_parts = line.split(',')
            alignment = style_parts[alignment_index].strip()
            if alignment in top_alignments:
                style_name = style_parts[0].replace('Style:', '').strip()
                top_styles.append(style_name)

    if not top_styles or not any(line.split(',')[3].strip() in top_styles for line in dialogue):
        top_styles = find_alignments_in_dialogue(dialogue, top_alignments)

    return top_styles

def find_alignments_in_dialogue(dialogue, top_alignments):
    dialogue_with_alignments = []
    for line in dialogue:
        if any(alignment in line for alignment in top_alignments) or '{\\an8}' in line:
            dialogue_with_alignments.append(line)
    return dialogue_with_alignments

def filter_dialogue_by_style(dialogue, top_styles):
    filtered_dialogue = [line for line in dialogue if line.split(',')[3].strip() in top_styles or '{\\an8}' in line]
    discarded_dialogue = [line for line in dialogue if line.split(',')[3].strip() not in top_styles and '{\\an8}' not in line]
    return filtered_dialogue, discarded_dialogue

# Scrive un file .ass per le righe "discarded_dialogue"
def write_discarded_ass_file(header, discarded_dialogue, format_line, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        # Scrive l'header e il formato degli eventi
        file.writelines(header + [format_line] + discarded_dialogue)

# Processa un file .ass
def process_ass_file(file_path, output_dir):
    lines = read_ass_file(file_path)
    header_section = []
    dialogue_section = []
    capture_dialogue = False
    capture_styles = False
    styles_section = []
    format_line_events = ""
    format_line_styles = ""

    for line in lines:
        if line.startswith('[V4+ Styles]'):
            capture_styles = True
            header_section.append(line)
            continue
        if line.startswith('[Events]'):
            capture_styles = False
            capture_dialogue = True
            header_section.append(line)
            continue
        if capture_dialogue and line.startswith('Dialogue:'):
            dialogue_section.append(line)
        elif not capture_dialogue:
            header_section.append(line)
        if capture_styles and line.startswith('Format:'):
            format_line_styles = line
        if not capture_styles and line.startswith('Format:'):
            format_line_events = line
        if capture_styles:
            styles_section.append(line)

    # Usa le funzioni per filtrare i dialoghi
    top_styles = find_top_alignments(styles_section, dialogue_section)
    filtered_dialogue, discarded_dialogue = filter_dialogue_by_style(dialogue_section, top_styles)

    # Percorsi di output
    output_ass_file_path = os.path.join(output_dir, 'On Top.ass')
    output_srt_file_path = os.path.join(output_dir, 'Sub.srt')
    discarded_ass_file_path = os.path.join(output_dir, 'Dialoghi.ass')

    # Scrive i file di output
    write_ass_file(header_section, filtered_dialogue, format_line_events, output_ass_file_path)
    write_srt_file_from_ass(discarded_dialogue, output_srt_file_path)
    write_discarded_ass_file(header_section, discarded_dialogue, format_line_events, discarded_ass_file_path)

    print(f'Sottotitoli processati e salvati in {output_ass_file_path}')
    print(f'Righe scartate salvate in {output_srt_file_path}')
    print(f'Righe scartate in formato ASS salvate in {discarded_ass_file_path}')

# Chiede se ci sono cartelli
def ask_about_signs():
    print("I sottotitoli che stai caricando hanno cartelli?")
    print("1: Sì")
    print("2: No")
    choice = input("Inserisci il numero della tua scelta: ").strip()
    return choice

# Funzione principale
def main():
    # Percorso relativo al progetto (esempio: Auto Sub ReTimer)
    project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    # Directory di output relativa
    output_dir = project_path

    choice = ask_about_signs()
    if choice == "1":
        print("Per una precisione maggiore, rimuovi i cartelli dai sottotitoli e riavvia lo script.")
    elif choice == "2":
        input_file_path = load_file()
        if input_file_path.endswith('.srt'):
            process_srt_file(input_file_path, output_dir)
        else:
            process_ass_file(input_file_path, output_dir)
    else:
        print("Scelta non valida. Riavvia lo script.")

if __name__ == '__main__':
    main()
