import os
import subprocess

# Percorso della directory principale del progetto
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Percorso dell'interprete Python nell'ambiente virtuale
venv_python = os.path.join(project_path, "main", "Scripts", "python.exe")

# Percorsi degli script
scripts_path = os.path.join(project_path, "Scripts", "Whisper Miglioramento Timing")
whispertiming_script = os.path.join(scripts_path, "whispertiming.py")
fase3_script = os.path.join(scripts_path, "Fase3.py")
fase4_script = os.path.join(scripts_path, "Fase4.py")

# File da eliminare per entrambi i casi
files_to_delete_general = [
    "scene_timestamps.srt",
    "scene_timestamps_adjusted.srt",
    "temp.wav",
    "vocali.wav",
    "whisper.aac",
    "whisper.srt",
    "whisper_adjusted.srt"
]

# File da eliminare specifici per la scelta "No"
files_to_delete_no = [
    "whisper.srt",
    "whisper.aac",
    "vocali.wav",
    "temp.wav"
]

# File da spostare sul Desktop per ciascun caso
files_to_move_yes = [
    "ep.mkv",
    "Final.srt"
]
files_to_move_no = [
    "whisper_adjusted.srt"
]

# Percorso del Desktop dell'utente
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

# Funzione per eseguire uno script Python
def esegui_script(script_path):
    if not os.path.exists(script_path):
        print(f"Errore: Lo script '{script_path}' non esiste!")
        exit(1)
    try:
        print(f"Esecuzione dello script: {script_path}...")
        subprocess.run([venv_python, script_path], check=True)
        print(f"Completato: {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'esecuzione dello script {script_path}: {e}")
        exit(1)

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

# Funzione per pulire tutte le directory __pycache__
def pulisci_pycache(directory):
    for root, dirs, files in os.walk(directory):
        for d in dirs:
            if d == "__pycache__":
                path = os.path.join(root, d)
                print(f"Svuotando la cache nella cartella: {path}")
                for file in os.listdir(path):
                    file_path = os.path.join(path, file)
                    try:
                        os.remove(file_path)
                        print(f"File eliminato: {file_path}")
                    except Exception as e:
                        print(f"Errore nel rimuovere {file_path}: {e}")

# 1. Verifica se esiste il file whispertiming.py ed eseguilo
esegui_script(whispertiming_script)

# 2. Chiedi all'utente cosa fare successivamente
while True:
    print("\nVuoi che i sottotitoli rispettino i cambio scena?")
    print("1) Sì")
    print("2) No")
    scelta = input("Inserisci il numero della tua scelta: ")

    if scelta == "1":
        # Esegui Fase3.py e Fase4.py in sequenza
        esegui_script(fase3_script)
        esegui_script(fase4_script)
        print("Operazione completata.")

        # Elimina i file generali
        print("Eliminazione dei file generali...")
        elimina_file(files_to_delete_general, project_path)

        # Sposta i file specificati per la scelta "Sì" sul Desktop
        print("Spostamento dei file sul Desktop (opzione 1)...")
        sposta_file(files_to_move_yes, project_path, desktop_path)

        break

    elif scelta == "2":
        print("Operazione completata senza modifiche ai sottotitoli.")

        # Elimina solo i file specifici per la scelta "No"
        print("Eliminazione dei file specificati per opzione 'No'...")
        elimina_file(files_to_delete_no, project_path)

        # Sposta i file specificati per la scelta "No" sul Desktop
        print("Spostamento dei file sul Desktop (opzione 2)...")
        sposta_file(files_to_move_no, project_path, desktop_path)

        break

    else:
        print("Scelta non valida. Per favore inserisci '1' o '2'.")

# 3. Pulizia delle cache
print("Pulizia delle cache...")
pulisci_pycache(project_path)
print("Pulizia completata.")
