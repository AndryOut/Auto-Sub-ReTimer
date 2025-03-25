# Automatic-Timing-Sub-Fix

NOT UPDATED LIKE THE .PY FILES

PHASE 1 REQUIREMENTS
- THE SUBS YOU ARE ABOUT TO UPLOAD MUST NOT HAVE SIGN.
- Upload a .ass or .srt file for line separation with alignment at the top of the screen and lines that are not. 
- When it's done, the only file you need is "Sub.srt," which must be reloaded into the next script.
(To avoid having too many files around, save only the local files "On Top" and "Sub," then delete everything else.)

PHASE 2 REQUIREMENTS
- THE SPOKEN AUDIO MUST BE ENTIRELY WITHIN THE LINES AND NOT PARTIALLY OUTSIDE THE LINE (Audio Spectrum). 
THIS MEANS THERE MUST NOT BE SPOKEN AUDIO STARTING BEFORE THE LINE, FOR EXAMPLE.
EVEN A QUICK SYNC THAT'S THE SAME FOR ALL LINES IS SUFFICIENT.

- UPLOAD THE EPISODE AUDIO HERE: https://huggingface.co/spaces/abidlabs/music-separation
AND DOWNLOAD ONLY THE "VOCALS."
THEN RENAME THE JUST-DOWNLOADED AUDIO TO "Vocali.wav."

- In Phase 2, you will first need to upload the episode audio with only the "vocals" (check requirements) and then the file "Sub.srt" from Phase 1.

- Once Phase 2 is completed, you can delete "temp.wav" and "Sub.srt" from Phase 1.

- However, do not delete "Vocali" and "adjusted_Sub.srt" from Colab.

PHASE 3 REQUIREMENTS
- Upload the video renamed to "Ep.mkv" on Colab (on Colab because it uploads faster than through the script).
(If it's a small-sized video, even better; it uploads faster, but don't reduce the quality too much.)

- Once Phase 3 is finished, you will have two outputs, "scene-timestamps.srt" (which you can also delete) and "scene_timestamps_adjusted.srt," which you must keep uploaded on Colab.
You can also delete "Ep.mkv" as it is no longer needed.

PHASE 4
If you have followed the previous instructions, you will end up with a file "Final.srt."
