import os
import subprocess

# Funzione per pulire tutte le directory __pycache__
def pulisci_pycache(directory):
    """
    Questa funzione elimina tutti i file all'interno delle cartelle __pycache__
    senza eliminare le cartelle stesse.
    """
    for root, dirs, files in os.walk(directory):
        for d in dirs:
            if d == "__pycache__":
                path = os.path.join(root, d)
                print(f"Svuotando la cache nella cartella: {path}")
                for file in os.listdir(path):
                    file_path = os.path.join(path, file)
                    try:
                        os.remove(file_path)  # Elimina ogni file all'interno della cartella
                        print(f"File eliminato: {file_path}")
                    except Exception as e:
                        print(f"Errore nel rimuovere {file_path}: {e}")

# Funzione per eliminare i file specificati
def elimina_file(files_to_delete, base_path):
    """
    Elimina i file specificati nella lista files_to_delete dalla directory base_path.
    """
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
    """
    Sposta i file specificati nella lista files_to_move dalla directory base_path al desktop.
    """
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
    """
    Controlla se tutti i file specificati nella lista esistono nella directory base_path.
    """
    return all(os.path.exists(os.path.join(base_path, file)) for file in files)

# Percorso della directory principale del progetto (relativa)
project_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

# Percorso del Desktop dell'utente (calcolato dinamicamente)
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

# Percorso dell'interprete Python nell'ambiente virtuale
venv_python = os.path.join(project_path, "main", "Scripts", "python.exe")

# Percorsi degli script delle fasi
fasi_path = os.path.join(project_path, "Scripts", "Migliora il Timing Dei Sub")
fase1_script = os.path.join(fasi_path, "Fase1.py")
fase2_script = os.path.join(fasi_path, "Fase2.py")
fase3_script = os.path.join(fasi_path, "Fase3.py")
fase4_script = os.path.join(fasi_path, "Fase4.py")
fase5_script = os.path.join(fasi_path, "Fase5.py")

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

# Verifica che tutti gli script esistano
for script in [fase1_script, fase2_script, fase3_script, fase4_script]:
    if not os.path.exists(script):
        print(f"Errore: Il file \"{script}\" non esiste!")
        exit()

# Esegui gli script in sequenza
try:
    print("Avvio di Fase1.py...")
    subprocess.run([venv_python, fase1_script], check=True)
    print("Fase1.py completato con successo.")

    print("Avvio di Fase2.py...")
    subprocess.run([venv_python, fase2_script], check=True)
    print("Fase2.py completato con successo.")

    print("Avvio di Fase3.py...")
    subprocess.run([venv_python, fase3_script], check=True)
    print("Fase3.py completato con successo.")

    print("Avvio di Fase4.py...")
    subprocess.run([venv_python, fase4_script], check=True)
    print("Fase4.py completato con successo.")

    print("Avvio di Fase5.py...")
    subprocess.run([venv_python, fase5_script], check=True)
    print("Fase5.py completato con successo.")

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

    # Pulizia delle cache
    print("Pulizia delle cache...")
    pulisci_pycache(project_path)
    print("Pulizia completata.")

except subprocess.CalledProcessError as e:
    print(f"Errore durante l'esecuzione di uno script: {e}")
except Exception as e:
    print(f"Si è verificato un errore generale: {e}")