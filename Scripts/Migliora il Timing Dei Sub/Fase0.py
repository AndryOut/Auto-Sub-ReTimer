import os
import subprocess
import shutil
import torch

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

# Verifica che FFmpeg esista
if not os.path.isfile(ffmpeg_path):
    print(f"Errore: FFmpeg non trovato nel percorso '{ffmpeg_path}'.")
    exit()

# Nome fisso per il file audio WAV
audio_file = "audio.wav"
audio_path = os.path.join(output_dir, audio_file)

# Comando FFmpeg per estrarre e convertire l'audio
ffmpeg_command = f'"{ffmpeg_path}" -hide_banner -loglevel error -i "{input_path}" -vn -acodec pcm_s16le -ar 44100 -ac 2 "{audio_path}"'

try:
    print(f"Estrazione e conversione dell'audio...")
    subprocess.run(ffmpeg_command, shell=True, check=True)
    print(f"Audio estratto e convertito in: {audio_path}")
except subprocess.CalledProcessError as e:
    print(f"Errore durante il processo di estrazione/conversione: {e}")
    exit()

# Percorso per l'eseguibile Python dell'ambiente virtuale
python_executable = os.path.join(project_path, "main", "Scripts", "python.exe")

# Verifica se CUDA è disponibile e imposta device
device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cuda":
    print("Elaborazione su GPU (CUDA)...")
else:
    print("CUDA non disponibile. Elaborazione su CPU (più lenta)...")

# Comando per eseguire Demucs con device dinamico
demucs_command = f'"{python_executable}" -m demucs --two-stems=vocals -d {device} -o "{output_dir}" "{audio_path}"'

try:
    print(f"Esecuzione di Demucs: {demucs_command}")
    subprocess.run(demucs_command, shell=True, check=True)

    # Percorso della cartella generata automaticamente da Demucs
    demucs_output_dir = os.path.join(output_dir, "htdemucs", os.path.splitext(audio_file)[0])

    # Sposta il file `vocals.wav` nella directory principale, rinominandolo in "vocali.wav"
    vocals_file = os.path.join(demucs_output_dir, "vocals.wav")
    renamed_vocals_file = os.path.join(output_dir, "vocali.wav")
    if os.path.exists(vocals_file):
        shutil.move(vocals_file, renamed_vocals_file)
        print(f"`vocals.wav` rinominato in: {renamed_vocals_file}")

    # Rimuovi il file "no_vocals.wav"
    no_vocals_file = os.path.join(demucs_output_dir, "no_vocals.wav")
    if os.path.exists(no_vocals_file):
        os.remove(no_vocals_file)
        print(f"`no_vocals.wav` eliminato.")

    # Rimuovi il file originale "audio.wav"
    if os.path.exists(audio_path):
        os.remove(audio_path)
        print(f"`audio.wav` eliminato.")

    # Rimuovi la cartella `htdemucs`
    shutil.rmtree(os.path.join(output_dir, "htdemucs"))
    print("Cartella `htdemucs` eliminata.")

    print("Operazione completata! Rimasto solo `vocali.wav` nella directory principale.")
except subprocess.CalledProcessError as e:
    print(f"Errore durante l'esecuzione di Demucs: {e}")
    exit()