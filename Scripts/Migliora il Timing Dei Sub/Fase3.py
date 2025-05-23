import os
from scenedetect import open_video, SceneManager
from scenedetect.detectors import AdaptiveDetector
import pysrt
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from concurrent.futures import as_completed

# Percorso della directory principale del progetto (relativa)
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Funzione per esportare i risultati in formato SRT con precisione al millisecondo
def export_srt(scene_list, output_path='scene_timestamps.srt'):
    def seconds_to_timecode(seconds):
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"

    with open(output_path, 'w') as f:
        for i, scene in enumerate(scene_list):
            start_time = scene[0].get_seconds()
            end_time = scene[1].get_seconds() - 0.001  # Sottrai 1 millisecondo per evitare sovrapposizioni
            start_timecode = seconds_to_timecode(start_time)
            end_timecode = seconds_to_timecode(end_time)
            f.write(f"{i+1}\n")
            f.write(f"{start_timecode} --> {end_timecode}\n")
            f.write(f"Scene {i+1}\n\n")

# Funzione per calcolare la discrepanza costante
def calculate_discrepancy(scene_list, srt_path):
    subs = pysrt.open(srt_path, encoding='utf-8')
    discrepancies = []
    count = min(len(scene_list), len(subs))
    for i in range(count):
        scene_start = scene_list[i][0].get_seconds()
        subtitle_start = subs[i].start.ordinal / 1000
        discrepancy = scene_start - subtitle_start
        discrepancies.append(discrepancy)
    return sum(discrepancies) / len(discrepancies)

# Funzione per trovare l'offset più vicino ai valori predefiniti
def find_closest_offset(discrepancy, possible_offsets):
    return min(possible_offsets, key=lambda x: abs(x - discrepancy))

# Funzione per applicare un offset globale al file SRT
def apply_global_offset_to_srt(input_path, output_path, offset):
    def apply_offset(timecode, offset):
        timecode.ordinal += int(offset * 1000)  # Converte i secondi in millisecondi
        return timecode

    subs = pysrt.open(input_path, encoding='utf-8')
    for sub in subs:
        sub.start = apply_offset(sub.start, offset)
        sub.end = apply_offset(sub.end, offset)
    subs.save(output_path, encoding='utf-8')

# Funzione per trovare i segmenti del video da analizzare basati sui sottotitoli
def get_segments_to_analyze(srt_path, min_gap=5.0, margin=2.0):
    subs = pysrt.open(srt_path, encoding='utf-8')
    segments = []
    
    if not subs:
        return segments
    
    # Estendi il primo inizio e l'ultima fine per catturare le scene ai bordi
    first_start = max(0, subs[0].start.ordinal / 1000 - margin * 2)  # Margine doppio all'inizio
    last_end = subs[-1].end.ordinal / 1000 + margin * 2  # Margine doppio alla fine
    
    current_start = first_start
    last_end = subs[0].end.ordinal / 1000
    
    for i in range(1, len(subs)):
        current_sub = subs[i]
        gap = (current_sub.start.ordinal / 1000) - (subs[i-1].end.ordinal / 1000)
        
        if gap >= min_gap:
            # Estendi il segmento corrente con margine abbondante
            segments.append((current_start, subs[i-1].end.ordinal / 1000 + margin))
            # Inizia nuovo segmento con margine abbondante
            current_start = current_sub.start.ordinal / 1000 - margin
        
        last_end = current_sub.end.ordinal / 1000
    
    # Aggiungi l'ultimo segmento esteso
    segments.append((current_start, last_end + margin))
    
    return segments

# Funzione per processare un singolo segmento
def process_segment(args):
    segment, video_path, adaptive_threshold = args
    start_time, end_time = segment
    
    try:
        video = open_video(video_path)
        video.seek(max(0, start_time - 0.5))
        
        scene_manager = SceneManager()
        adaptive_detector = AdaptiveDetector(
            adaptive_threshold=adaptive_threshold,
            min_content_val=20
        )
        scene_manager.add_detector(adaptive_detector)
        
        scene_manager.detect_scenes(video, end_time=end_time + 0.5)
        
        segment_scenes = []
        for scene in scene_manager.get_scene_list():
            scene_start = scene[0].get_seconds()
            scene_end = scene[1].get_seconds()
            if scene_end > start_time and scene_start < end_time:
                segment_scenes.append(scene)
        
        return segment_scenes
    except Exception as e:
        print(f"Errore durante l'elaborazione del segmento {start_time}-{end_time}: {str(e)}")
        return []

def main():
    # Percorso del file video
    video_path = os.path.join(project_path, "ep.mkv")
    if not os.path.exists(video_path):
        raise FileNotFoundError("Il file video non è stato trovato.")

    # Percorso del file SRT dei sottotitoli
    srt_path = os.path.join(project_path, "adjusted_Sub.srt")
    if not os.path.exists(srt_path):
        raise FileNotFoundError("Il file SRT dei sottotitoli non è stato trovato.")

    # Ottieni i segmenti del video da analizzare
    segments = get_segments_to_analyze(srt_path, min_gap=5.0, margin=1.0)

    # Parametri per i detector
    adaptive_threshold = 3

    # Prepara gli argomenti per il pool
    process_args = [(segment, video_path, adaptive_threshold) for segment in segments]

    # Rilevamento parallelo delle scene
    print("Analisi parallela delle scene in corso...")
    total_segments = len(segments)
    num_threads = min(cpu_count(), len(segments)) if segments else 1  # Mantieni la tua logica originale
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(process_segment, arg) for arg in process_args]
        
        for i, _ in enumerate(as_completed(futures), 1):
            progress = int((i / total_segments) * 50)
            print("\rAnalisi scene: [{}{}] {:>3}%".format(
                '=' * progress,
                ' ' * (50 - progress),
                int((i / total_segments) * 100)), 
                end='', flush=True)
    
    print("\nAnalisi completata!")
    results = [future.result() for future in futures] 

    # Unisci i risultati
    all_scenes = []
    for segment_scenes in results:
        all_scenes.extend(segment_scenes)
    all_scenes.sort(key=lambda x: x[0].get_seconds())

    # Esporta i risultati
    srt_output_path = os.path.join(project_path, "scene_timestamps.srt")
    export_srt(all_scenes, output_path=srt_output_path)

    # Calcola e applica offset
    discrepancy = calculate_discrepancy(all_scenes, srt_output_path)
    possible_offsets = [-0.011, -0.021, -0.031, -0.041]
    best_offset = find_closest_offset(discrepancy, possible_offsets)
    adjusted_srt_output_path = os.path.join(project_path, "scene_timestamps_adjusted.srt")
    apply_global_offset_to_srt(srt_output_path, adjusted_srt_output_path, best_offset)

    # Stampa risultati
    print(f"Scene rilevate: {len(all_scenes)}")
    for i, scene in enumerate(all_scenes):
        print(f"Scena {i+1}: Inizio: {scene[0].get_timecode()}, Fine: {scene[1].get_timecode()}")
    print(f"File SRT con offset globale applicato creato con successo: scene_timestamps_adjusted.srt")
    print(f"Offset applicato: {best_offset:.3f} secondi")
    print(f"Segmenti analizzati: {segments}")

if __name__ == '__main__':
    main()