import os

# Funzione per pulire tutte le directory __pycache__
# (DISABILITATA - COMMENTATA)
# def pulisci_pycache(directory):
#     for root, dirs, files in os.walk(directory):
#         for d in dirs:
#             if d == "__pycache__":
#                 path = os.path.join(root, d)
#                 print(f"Svuotando la cache nella cartella: {path}")
#                 for file in os.listdir(path):
#                     file_path = os.path.join(path, file)
#                     try:
#                         os.remove(file_path)
#                         print(f"File eliminato: {file_path}")
#                     except Exception as e:
#                         print(f"Errore nel rimuovere {file_path}: {e}")

# Funzione per eliminare i file specificati
def elimina_file(files_to_delete, base_path):
    for file in files_to_delete:
        file_path = os.path.join(base_path, file)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"File eliminato: {file_path}")
            except Exception as e:
                print(f"Errore nel rimuovere {file_path}: {e}")
        else:
            print(f"Il file {file_path} non esiste.")

# Funzione per spostare i file specificati sul Desktop
def sposta_file(files_to_move, base_path, desktop_path):
    for file in files_to_move:
        src_path = os.path.join(base_path, file)
        dest_path = os.path.join(desktop_path, file)
        if os.path.exists(src_path):
            try:
                os.rename(src_path, dest_path)
                print(f"File spostato: {src_path} -> {dest_path}")
            except Exception as e:
                print(f"Errore nello spostare {src_path}: {e}")
        else:
            print(f"Il file {src_path} non esiste.")

# Funzione per verificare se un set di file è presente
def verifica_file(files, base_path):
    return all(os.path.exists(os.path.join(base_path, file)) for file in files)

# Percorso della directory principale del progetto (relativa)
project_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

# Percorso del Desktop dell'utente
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

# File da eliminare (prima opzione)
files_to_delete_option_1 = [
    "adjusted_Sub.srt",
    "scene_timestamps.srt",
    "scene_timestamps_adjusted.srt",
    "Sub.srt",
    "temp.wav",
    "vocali.wav",
    "Dialoghi.ass",
    "Final.srt"
]

# File da eliminare (seconda opzione)
files_to_delete_option_2 = [
    "adjusted_Sub.srt",
    "scene_timestamps.srt",
    "scene_timestamps_adjusted.srt",
    "Sub.srt",
    "temp.wav",
    "vocali.wav"
]

# File da spostare sul Desktop (prima opzione)
files_to_move_option_1 = [
    "ep.mkv",
    "On Top.ass",
    "Final.ass"
]

# File da spostare sul Desktop (seconda opzione)
files_to_move_option_2 = [
    "ep.mkv",
    "On Top.srt",
    "Final.srt"
]

# Esegui le operazioni di pulizia e spostamento
try:
    # Determina quale set di file spostare sul Desktop
    if verifica_file(files_to_move_option_1, project_path):
        print("Trovati i file del set 1. Spostamento in corso...")
        sposta_file(files_to_move_option_1, project_path, desktop_path)
        print("Eliminazione dei file specificati per il set 1...")
        elimina_file(files_to_delete_option_1, project_path)
    elif verifica_file(files_to_move_option_2, project_path):
        print("Trovati i file del set 2. Spostamento in corso...")
        sposta_file(files_to_move_option_2, project_path, desktop_path)
        print("Eliminazione dei file specificati per il set 2...")
        elimina_file(files_to_delete_option_2, project_path)
    else:
        print("Nessun set di file trovato per lo spostamento.")

    # Pulizia delle cache (DISABILITATA - COMMENTATA)
    # print("Pulizia delle cache...")
    # pulisci_pycache(project_path)
    # print("Pulizia completata.")

except Exception as e:
    print(f"Si è verificato un errore generale: {e}")