@echo off

cd /d "%~dp0"

set exe_folder=Faster-Whisper-XXL
set exe_file=faster-whisper-xxl.exe
set input_file=whisper.aac
set output_dir=.

cd "%exe_folder%"

echo Ora eseguo whisper...

%exe_file% "..\%input_file%" --language ja --model medium --vad_filter True --vad_method pyannote_onnx_v3 --sentence --word_timestamps True --clip_timestamps 1 --no_speech_threshold 0.1 --condition_on_previous_text False --vad_min_silence_duration_ms 100 --output_dir ".."

if %ERRORLEVEL% NEQ 0 (
    echo Finito...
)

:: Pausa finale per verificare il risultato
pause
