import pysrt
from pydub import AudioSegment
import librosa
import os

# Percorso della directory principale
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# File di input
audio_file = os.path.join(project_dir, "vocali.wav")
srt_file = os.path.join(project_dir, "whisper.srt")

# File di output
output_file = os.path.join(project_dir, 'whisper_adjusted.srt')

# Funzione per convertire i millisecondi in SubRipTime
def milliseconds_to_subrip_time(milliseconds):
    hours = int(milliseconds // 3600000)
    minutes = int((milliseconds % 3600000) // 60000)
    seconds = int((milliseconds % 60000) // 1000)
    milliseconds = int(milliseconds % 1000)
    return pysrt.SubRipTime(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)

# Funzione per rilevare i segmenti audio con Pydub e Librosa
def get_audio_segments(audio_file, silence_threshold=320):
    # Carica l'audio con Pydub
    audio = AudioSegment.from_file(audio_file)
    temp_audio_file = os.path.join(project_dir, "temp.wav")
    audio.export(temp_audio_file, format="wav")

    # Carica l'audio con Librosa
    temp_audio_file = os.path.join(project_dir, "temp.wav")
    y, sr = librosa.load(temp_audio_file, sr=None)

    # Rileva i segmenti non silenziosi
    intervals = librosa.effects.split(y, top_db=20)

    # Converte i segmenti in millisecondi
    segments = []
    for start, end in intervals:
        segments.append((start / sr * 1000, end / sr * 1000))

    return segments

# Funzione per aggiungere lead-in partendo dal picco
def add_lead_in_to_peak_or_previous(subs, audio_file, lead_in=150):
    audio_segments = get_audio_segments(audio_file)
    for sub in subs:
        start_ms = sub.start.ordinal

        # Controlla se il timestamp iniziale coincide con un picco audio
        found_peak = False
        for segment_start, segment_end in audio_segments:
            if segment_start <= start_ms <= segment_end:
                # Aggiungi lead-in basandoti su questo picco
                sub.start = milliseconds_to_subrip_time(max(0, segment_start - lead_in))
                found_peak = True
                break

        # Se non è già su un picco, cerca un picco precedente entro 0,300 secondi
        if not found_peak:
            for segment_start, segment_end in reversed(audio_segments):  # Itera al contrario per cercare i picchi precedenti
                if segment_start < start_ms and (start_ms - segment_start) <= 300:
                    # Modifica il timestamp per aggiungere il lead-in basandoti sul picco precedente
                    sub.start = milliseconds_to_subrip_time(max(0, segment_start - lead_in))
                    break

    return subs

# Funzione per collegare segmenti senza overlap con spazio di 0,000 secondi
def adjust_segments_for_overlap(segments, max_lead_out=200, lead_in=30, max_lead_in=50, lead_out=100):
    adjusted_segments = []
    for i in range(len(segments) - 1):
        start, end = segments[i]
        next_start, next_end = segments[i + 1]

        if (next_start - end) <= max_lead_out:
            if (next_start - end) > lead_out:
                remaining_time = next_start - end - lead_out
                end = next_start - remaining_time  # collega con spazio di 0,000 secondi
            else:
                end = next_start  # collega con spazio di 0,000 secondi
        else:
            if (next_start - end) > lead_in and (next_start - end) < max_lead_in:
                end = next_start - lead_in

        adjusted_segments.append((start, end))

    adjusted_segments.append(segments[-1])
    return adjusted_segments

# Verifica se i file di input esistono
if not os.path.exists(audio_file):
    print(f"Errore: il file audio {audio_file} non esiste.")
    exit(1)

if not os.path.exists(srt_file):
    print(f"Errore: il file SRT {srt_file} non esiste.")
    exit(1)

# Carica il file SRT originale
subs = pysrt.open(srt_file, encoding='utf-8')

# Aggiunge il lead-in partendo dal picco attuale o precedente
subs = add_lead_in_to_peak_or_previous(subs, audio_file)

# Ottieni i segmenti originali con gli orari aggiornati
final_segments = [(sub.start.ordinal, sub.end.ordinal) for sub in subs]

# Regola i segmenti per evitare sovrapposizioni
adjusted_segments = adjust_segments_for_overlap(final_segments)

# Applica i segmenti regolati ai sottotitoli
for sub, (start, end) in zip(subs, adjusted_segments):
    sub.start = milliseconds_to_subrip_time(start)
    sub.end = milliseconds_to_subrip_time(end)

# Salva il file SRT finale
subs.save(output_file, encoding='utf-8')

print(f"File SRT salvato come {output_file}")
