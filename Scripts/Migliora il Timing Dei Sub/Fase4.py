import pysrt
from pydub import AudioSegment
import librosa
import numpy as np
import os
import json

# Percorso della directory principale del progetto (relativa)
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# =============================================
# CARICAMENTO PARAMETRI CONFIGURABILI DA JSON
# =============================================
CONFIG_PATH = os.path.join(project_path, "Scripts", "Migliora il Timing Dei Sub", "Config_Fase4.json")

# Valori di default
DEFAULT_CONFIG = {
    "max_range_next_scene": 300
}

try:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    MAX_RANGE_NEXT_SCENE = config.get("max_range_next_scene", DEFAULT_CONFIG["max_range_next_scene"])
except (FileNotFoundError, json.JSONDecodeError):
    MAX_RANGE_NEXT_SCENE = DEFAULT_CONFIG["max_range_next_scene"]

# =============================================
# FUNZIONI PRINCIPALI
# =============================================

def milliseconds_to_subrip_time(milliseconds):
    hours = int(milliseconds // 3600000)
    minutes = int((milliseconds % 3600000) // 60000)
    seconds = int((milliseconds % 60000) // 1000)
    milliseconds = int(milliseconds % 1000)
    return pysrt.SubRipTime(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)

def get_audio_peaks(audio_file):
    y, sr = librosa.load(audio_file)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    peaks = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, backtrack=True)
    peak_times = librosa.frames_to_time(peaks, sr=sr)
    return peak_times

def adjust_subs_based_on_scenes(original_subs, scene_subs):
    adjusted_subs = original_subs
    for idx, sub in enumerate(adjusted_subs):
        start_replaced = False
        for scene in reversed(scene_subs):
            scene_end = scene.end.ordinal
            sub_start = sub.start.ordinal
            if 0 < (sub_start - scene_end) <= 200:
                sub.start = milliseconds_to_subrip_time(scene_end)
                start_replaced = True
                break
        if idx > 0:
            prev_sub = adjusted_subs[idx - 1]
            prev_sub_end = prev_sub.end.ordinal
            prev_sub_start = prev_sub.start.ordinal
            if prev_sub_end > scene_end and scene_end >= prev_sub_start:
                if start_replaced:
                    prev_sub.end = milliseconds_to_subrip_time(scene_end - 0)
            else:
                if scene_end >= prev_sub_end:
                    if start_replaced:
                        sub.start = milliseconds_to_subrip_time(scene_end)
                if not start_replaced:
                    prev_sub.end = milliseconds_to_subrip_time(prev_sub_end)
    return adjusted_subs

def adjust_sub_start_based_on_scene_change(original_subs, scene_subs):
    for sub in original_subs:
        sub_start = sub.start.ordinal
        for scene in scene_subs:
            scene_start = scene.start.ordinal
            if 0 < (scene_start - sub_start) <= 200:
                sub.start = milliseconds_to_subrip_time(scene_start)
                break
    return original_subs

def add_lead_in_to_peaks(subs, audio_peaks):
    min_lead_in = 10
    max_lead_in = 20
    additional_lead_in = 30
    gap_threshold = 300

    for idx, sub in enumerate(subs):
        sub_start = sub.start.ordinal
        for peak in audio_peaks:
            peak_time = int(peak * 1000)
            lead_in_duration = peak_time - sub_start
            if 0 < lead_in_duration < min_lead_in:
                sub.start = milliseconds_to_subrip_time(sub_start - additional_lead_in)
                break
            elif min_lead_in <= lead_in_duration <= max_lead_in:
                break
        if idx > 0:
            prev_sub_end = subs[idx - 1].end.ordinal
            if sub.start.ordinal < prev_sub_end:
                sub.start = milliseconds_to_subrip_time(prev_sub_end + 0)
        if idx < len(subs) - 1:
            next_sub_start = subs[idx + 1].start.ordinal
            if 0 < (next_sub_start - sub.end.ordinal) <= gap_threshold:
                sub.end = milliseconds_to_subrip_time(next_sub_start)

    return subs

def add_lead_in_based_on_conditions(subs, scene_subs):
    min_duration = 100
    max_duration = 1500
    lead_in_increment = 100
    range_previous_line = 50

    for idx, sub in enumerate(subs):
        sub_end = sub.end.ordinal
        sub_start = sub.start.ordinal
        sub_duration = sub_end - sub_start

        is_above_scene_change = False
        for scene in scene_subs:
            scene_end = scene.end.ordinal
            if sub_start <= scene_end <= sub_end:
                is_above_scene_change = True
                break

        if is_above_scene_change and min_duration <= sub_duration <= max_duration:
            is_start_on_scene = any(
                scene.start.ordinal == sub_start for scene in scene_subs
            )
            if not is_start_on_scene:
                has_previous_line_in_range = False
                if idx > 0:
                    previous_sub_end = subs[idx - 1].end.ordinal
                    if sub_start - previous_sub_end <= range_previous_line:
                        has_previous_line_in_range = True

                if not has_previous_line_in_range:
                    sub.start = milliseconds_to_subrip_time(
                        sub_start - lead_in_increment
                    )

    return subs

def adjust_sub_end_based_on_next_scene_change(original_subs, scene_subs):
    # Modificato: 300 -> MAX_RANGE_NEXT_SCENE
    for idx, sub in enumerate(original_subs):
        sub_end = sub.end.ordinal
        for scene in scene_subs:
            scene_start = scene.start.ordinal
            if 0 < (scene_start - sub_end) <= MAX_RANGE_NEXT_SCENE:
                if idx < len(original_subs) - 1 and original_subs[idx + 1].start.ordinal < scene_start:
                    break
                sub.end = milliseconds_to_subrip_time(scene_start)
                break

    return original_subs

def adjust_sub_end_based_on_previous_scene_change(original_subs, scene_subs, audio_peaks):
    max_range = 900
    extra_range_after_scene = 120

    for sub in original_subs:
        sub_end = sub.end.ordinal
        sub_start = sub.start.ordinal
        for scene in reversed(scene_subs):
            scene_end = scene.end.ordinal
            if sub_start <= scene_end <= sub_end and 0 < (sub_end - scene_end) <= max_range:
                peaks_count = 0
                for peak in audio_peaks:
                    peak_time = int(peak * 1000)
                    if scene_end <= peak_time <= sub_end:
                        peaks_count += 1

                if peaks_count <= 1:
                    sub.end = milliseconds_to_subrip_time(scene_end)
                break

    return original_subs

# =============================================
# ESECUZIONE PRINCIPALE 
# =============================================
original_subs = pysrt.open(os.path.join(project_path, 'adjusted_Sub.srt'), encoding='utf-8')
scene_subs = pysrt.open(os.path.join(project_path, 'scene_timestamps_adjusted.srt'), encoding='utf-8')
audio_peaks = get_audio_peaks(os.path.join(project_path, 'vocali.wav'))

adjusted_subs = add_lead_in_to_peaks(original_subs, audio_peaks)
adjusted_subs = adjust_subs_based_on_scenes(original_subs, scene_subs)
adjusted_subs = adjust_sub_start_based_on_scene_change(original_subs, scene_subs)
adjusted_subs = adjust_sub_end_based_on_next_scene_change(original_subs, scene_subs)
adjusted_subs = adjust_sub_end_based_on_previous_scene_change(adjusted_subs, scene_subs, audio_peaks)
adjusted_subs = add_lead_in_based_on_conditions(adjusted_subs, scene_subs)

adjusted_subs.save(os.path.join(project_path, 'Final.srt'), encoding='utf-8')
print("Script completato e sottotitoli aggiornati salvati come 'Final.srt'")