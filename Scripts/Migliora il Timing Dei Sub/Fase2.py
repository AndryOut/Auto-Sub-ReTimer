import pysrt
from pydub import AudioSegment
import librosa
import numpy as np
import os

# Percorso della directory principale del progetto (relativa)
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

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
    temp_file = os.path.join(project_path, "temp.wav")
    audio.export(temp_file, format="wav")


    # Carica l'audio con Librosa
    y, sr = librosa.load(temp_file, sr=None)

    # Rileva i segmenti non silenziosi
    intervals = librosa.effects.split(y, top_db=20)

    # Converte i segmenti in millisecondi
    segments = []
    for start, end in intervals:
        segments.append((start / sr * 1000, end / sr * 1000))

    return segments

# Funzione per rilevare i picchi audio per aggiustare i time stamps
def adjust_timestamps_based_on_peaks(subs, audio_file):
    audio_segments = get_audio_segments(audio_file)
    for sub in subs:
        start_ms = sub.start.ordinal
        end_ms = sub.end.ordinal

        # Trova il primo picco audio dopo l'inizio del time stamp
        for segment_start, segment_end in audio_segments:
            if segment_start >= start_ms:
                if segment_start - start_ms > 150:
                    found = False
                    for closer_segment_start, closer_segment_end in audio_segments:
                        if start_ms <= closer_segment_start <= start_ms + 100:
                            sub.start = milliseconds_to_subrip_time(closer_segment_start)
                            found = True
                            break
                    if not found:
                        sub.start = milliseconds_to_subrip_time(start_ms)
                else:
                    sub.start = milliseconds_to_subrip_time(segment_start)
                break

        # Se il time stamp finale è già su un picco audio, mantiene il valore originale
        is_on_peak = any(segment_start <= end_ms <= segment_end for segment_start, segment_end in audio_segments)

        if not is_on_peak:  # Cerca un picco solo se non è già su un picco
            max_ranges = [600, 600]
            for max_range in max_ranges:
                found = False
                for segment_start, segment_end in reversed(audio_segments):
                    if segment_end <= end_ms and segment_start >= start_ms:
                        if end_ms - segment_end <= max_range:
                            sub.end = milliseconds_to_subrip_time(segment_end)
                            found = True
                            break
                if found:
                    break

            # Se il picco audio rilevato è troppo lontano, lo cerca di nuovo
            if end_ms - sub.end.ordinal > 600:
                for segment_start, segment_end in audio_segments:
                    if segment_end <= end_ms and segment_start >= start_ms:
                        if end_ms - segment_end <= 300:
                            sub.end = milliseconds_to_subrip_time(segment_end)
                            break
                else:
                    sub.end = milliseconds_to_subrip_time(end_ms)

    return subs

# Funzione per aggiungere lead-in e lead-out ai segmenti
def add_lead_in_out(segments, original_subs, lead_in=200, lead_out=500):
    adjusted_segments = []
    for i, (start, end) in enumerate(segments):
        original_start_ms = original_subs[i].start.ordinal
        if start == original_start_ms:
            new_start = start  # Non aggiungere lead-in se è uguale al time stamp originale
        else:
            new_start = max(0, start - lead_in)  # Aggiungi lead-in altrimenti
        new_end = end + lead_out  # Aggiungi lead-out a tutto
        adjusted_segments.append((new_start, new_end))
    return adjusted_segments

# Funzione per collegare segmenti senza overlap con spazio di 0,000 secondi
def adjust_segments_for_overlap(segments, max_lead_out=50, lead_in=30, max_lead_in=50, lead_out=30):
    adjusted_segments = []
    for i in range(len(segments) - 1):
        start, end = segments[i]
        next_start, next_end = segments[i + 1]

        if (next_start - end) <= max_lead_out:
            if (next_start - end) > lead_out:
                remaining_time = next_start - end - lead_out
                end = next_start - remaining_time 
            else:
                end = next_start  
        else:
            if (next_start - end) > lead_in and (next_start - end) < max_lead_in:
                end = next_start - lead_in

        adjusted_segments.append((start, end))

    adjusted_segments.append(segments[-1])
    return adjusted_segments

# Specifica i file direttamente
audio_file = os.path.join(project_path, "vocali.wav")
srt_file = os.path.join(project_path, "Sub.srt")

# Carica il file SRT originale
subs = pysrt.open(srt_file, encoding='utf-8')
original_subs = pysrt.open(srt_file, encoding='utf-8')

# Aggiusta i time stamps delle righe in base ai picchi audio rilevati
subs = adjust_timestamps_based_on_peaks(subs, audio_file)

# Ottieni i segmenti audio con Pydub e Librosa
audio_segments = get_audio_segments(audio_file)

# Non unisce i segmenti, mantiene solo quelli esistenti
final_segments = [(sub.start.ordinal, sub.end.ordinal) for sub in subs]

# Aggiunge lead-in e lead-out ai segmenti
adjusted_segments = add_lead_in_out(final_segments, original_subs)

# Regola i segmenti per evitare overlap e collegarli con spazio di 0,000 secondi
adjusted_segments = adjust_segments_for_overlap(adjusted_segments)

# Crea il file SRT basato sui segmenti finali e mantiene il testo originale
for sub, (start, end) in zip(subs, adjusted_segments):
    sub.start = milliseconds_to_subrip_time(start)
    sub.end = milliseconds_to_subrip_time(end)

# Salva il file SRT finale
output_file = os.path.join(project_path, "adjusted_Sub.srt")
subs.save(output_file, encoding='utf-8')

print(f"File SRT salvato come {output_file}")
