import os
from scenedetect import open_video, SceneManager
from scenedetect.detectors import AdaptiveDetector, ContentDetector
import pysrt

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

# Percorso del file video
video_path = os.path.join(project_path, "ep.mkv")
if not os.path.exists(video_path):
    raise FileNotFoundError("Il file video non è stato trovato.")

# Caricamento del video
video_manager = open_video(video_path)

# SceneManager con AdaptiveDetector e ContentDetector
scene_manager = SceneManager()
adaptive_detector = AdaptiveDetector(adaptive_threshold=19)
content_detector = ContentDetector(threshold=19)
scene_manager.add_detector(adaptive_detector)
scene_manager.add_detector(content_detector)

# Rileva le scene
scene_manager.detect_scenes(video_manager)
scene_list = scene_manager.get_scene_list()

# Esporta i risultati in formato SRT
srt_output_path = os.path.join(project_path, "scene_timestamps.srt")
export_srt(scene_list, output_path=srt_output_path)

# Calcola la discrepanza costante
discrepancy = calculate_discrepancy(scene_list, srt_output_path)

# Offset possibili
possible_offsets = [-0.011, -0.021, -0.031, -0.041]

# Trova l'offset più vicino
best_offset = find_closest_offset(discrepancy, possible_offsets)

# Applica l'offset globale al file SRT
adjusted_srt_output_path = os.path.join(project_path, "scene_timestamps_adjusted.srt")
apply_global_offset_to_srt(srt_output_path, adjusted_srt_output_path, best_offset)

# Stampa i risultati
print(f"Scene rilevate: {len(scene_list)}")
for i, scene in enumerate(scene_list):
    print(f"Scena {i+1}: Inizio: {scene[0].get_timecode()}, Fine: {scene[1].get_timecode()}")
print(f"File SRT con offset globale applicato creato con successo: scene_timestamps_adjusted.srt")
print(f"Offset applicato: {best_offset:.3f} secondi")
