As with "Auto Sub ReTimer" on Colab, there are requirements.

- Put your episode renamed to "ep.mkv" inside the "Auto Sub ReTimer" folder.

- Go to the site "https://huggingface.co/spaces/abidlabs/music-separation" and upload the episode audio.
 - When the process is finished, download the "Vocals" audio.
  - Rename the downloaded audio to "vocali.wav" and place it in the "Auto Sub ReTimer" folder along with "ep.mkv".
 
 - Now the most important requirement, as with Colab...                                         
    THE SPOKEN AUDIO MUST BE ENTIRELY WITHIN THE LINES AND NOT PARTIALLY OUTSIDE THE LINE       
    (Audio Spectrum).                                                                           
    THERE MUST NOT BE THE START OF SPOKEN AUDIO THAT BEGINS BEFORE THE LINE, FOR EXAMPLE.       
    WHEN UPLOADING YOUR .ASS OR .SRT, MAKE SURE TO FOLLOW THE INSTRUCTIONS.                     
    EVEN A QUICK SYNC THAT'S THE SAME FOR ALL LINES IS SUFFICIENT.                              
    FOR EXAMPLE -0.050 OR -0.100. WITH VALUES TOO HIGH YOU WILL GET THE OPPOSITE EFFECT.        


- Run "Auto Sub ReTimer.bat".
 - In Phase 1 it will ask you to select the subtitles you want to adjust, BUT WITHOUT SIGNS!
  - Once finished, you will find "ep.mkv", "On Top.ass/.srt" and "Final.srt/.ass" on the desktop.
   - If "On Top" is empty, then there were no lines aligned at the top.

-------------------------------------------------------------------------------------------------

To use whisper.

REQUIREMENTS

-Extract the audio from your episode, rename it to "whisper.aac" and place it in the "Auto Sub ReTimer" folder.
 (you can change the ".aac" extension by modifying "Whisper.bat").
 - If you intend to improve the timing of whisper then you will need the "Vocals".
   Go to the site "https://huggingface.co/spaces/abidlabs/music-separation" and upload the episode audio.
   When the process is finished, download the "Vocals" audio.
   Rename the downloaded audio to "vocali.wav" and place it in the "Auto Sub ReTimer" folder.
   If you want it to also respect scene changes, then you will also need the episode renamed to "ep.mkv" in "Auto Sub ReTimer".

- You must first use "Whisper.bat", it will download everything needed (the default model is "medium").
  (you can modify the model in "Whisper.bat").

- When it is finished, you will find "whisper.srt".

- To improve the timing of "whisper.srt" you will need to use "Whisper ReTimer.bat".
 - You will have two options: use only a basic timing improvement or ensure it also respects scene changes.
  - Once you have made your choice and the process is complete, you will find everything you need on the desktop.
   (Keep in mind that the improvement with scene changes is not perfect, especially if used with the basic timing of whisper).
