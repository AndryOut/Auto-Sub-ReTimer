import os
import subprocess

# Percorso relativo al progetto
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Nome del file MKV di input
input_file = "ep.mkv"

# Directory di input/output basata su project_path
input_path = os.path.join(project_path, input_file)
output_dir = project_path

# Verifica che il file MKV esista
if not os.path.isfile(input_path):
    print(f"Errore: Il file '{input_file}' non esiste nella directory '{project_path}'.")
    exit()

# Percorso relativo per FFmpeg
ffmpeg_path = os.path.join(project_path, "ffmpeg", "bin", "ffmpeg.exe")
ffprobe_path = os.path.join(project_path, "ffmpeg", "bin", "ffprobe.exe")

# Verifica che FFmpeg e ffprobe esistano
if not os.path.isfile(ffmpeg_path):
    print(f"Errore: FFmpeg non trovato nel percorso '{ffmpeg_path}'.")
    exit()
if not os.path.isfile(ffprobe_path):
    print(f"Errore: FFprobe non trovato nel percorso '{ffprobe_path}'.")
    exit()

# Nome del file finale .aac
audio_file = "whisper.aac"
audio_path = os.path.join(output_dir, audio_file)

# Comando ffprobe per verificare il codec audio del file input
ffprobe_command = f'"{ffprobe_path}" -hide_banner -loglevel error -select_streams a -show_entries stream=codec_name -of csv=p=0 "{input_path}"'

try:
    print("Verifica del codec audio del file di input...")
    result = subprocess.run(ffprobe_command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    codec = result.stdout.strip()
    print(f"Codec rilevato: {codec}")

    # Se il file è già in formato AAC, lo estrae
    if codec == "aac":
        print("L'audio è già in formato AAC. Estrazione senza conversione...")
        ffmpeg_command = f'"{ffmpeg_path}" -hide_banner -loglevel error -i "{input_path}" -vn -acodec copy "{audio_path}"'
    else:
        # Converte l'audio in formato AAC
        print("Convertendo l'audio in formato AAC...")
        ffmpeg_command = f'"{ffmpeg_path}" -hide_banner -loglevel error -i "{input_path}" -vn -acodec aac -b:a 192k "{audio_path}"'

    subprocess.run(ffmpeg_command, shell=True, check=True)
    print(f"Operazione completata. File audio salvato come: {audio_path}")

except subprocess.CalledProcessError as e:
    print(f"Errore durante il processo di estrazione/conversione: {e}")
    exit()
