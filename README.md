Do you want to change the values ​​according to your preferences?  
[Read here](Scripts/Migliora%20il%20Timing%20Dei%20Sub/README.md)

As with "Auto Sub ReTimer" on Colab, there are requirements.

- Put your episode renamed to "ep.mkv" inside the "Auto Sub ReTimer" folder.

- Go to the site "https://huggingface.co/spaces/abidlabs/music-separation" and upload the episode audio.
 - When the process is finished, download the "Vocals" audio.
  - Rename the downloaded audio to "vocali.wav" and place it in the "Auto Sub ReTimer" folder along with "ep.mkv".

Example:

![Example](https://github.com/user-attachments/assets/67cb11ee-79b4-471d-9038-e94ddb60d95b)

 
 - Now the most important requirement, as with Colab...                                         
    THE SPOKEN AUDIO MUST BE ENTIRELY WITHIN THE LINES AND NOT PARTIALLY OUTSIDE THE LINE       
    (Audio Spectrum).                                                                           
    THERE MUST NOT BE THE START OF SPOKEN AUDIO THAT BEGINS BEFORE THE LINE, FOR EXAMPLE.       
    WHEN UPLOADING YOUR .ASS OR .SRT, MAKE SURE TO FOLLOW THE INSTRUCTIONS.                     
    EVEN A QUICK SYNC THAT'S THE SAME FOR ALL LINES IS SUFFICIENT.                              
    FOR EXAMPLE -0.050 OR -0.100. WITH VALUES TOO HIGH YOU WILL GET THE OPPOSITE EFFECT.        

Does not meet the requirements:

![Does not meet the requirements](https://github.com/user-attachments/assets/5e963886-c763-4511-a35a-716d4dba95cb)

Meets the requirements:

![Meets the requirements](https://github.com/user-attachments/assets/faace722-7cc3-400f-944a-2be206f7c0e6)


- Run "Auto Sub ReTimer.bat".
 - In Phase 1 it will ask you to select the subtitles you want to adjust, BUT WITHOUT SIGNS!
  - Once finished, you will find "ep.mkv", "On Top.ass/.srt" and "Final.srt/.ass" on the desktop.
   - If "On Top" is empty, then there were no lines aligned at the top.

Before and after examples Auto Sub ReTimer:

Example 1 Original Sub:

![Original](https://github.com/user-attachments/assets/7953eb46-e2ed-49ff-b1b0-3c997a78c0f5)
![Original](https://github.com/user-attachments/assets/5e3d6209-8601-4ecd-a9e7-ebd7289b724a)

Adjusted Sub with scene change:

![Adjusted](https://github.com/user-attachments/assets/780d6aa0-d7bc-4ee8-865d-38849dd6d892)
![Adjusted](https://github.com/user-attachments/assets/516aff27-5ab5-4e00-a75c-7ac88594b317)

Example 2 Original Sub:

![Original](https://github.com/user-attachments/assets/ed23556d-9766-44eb-a9cb-a20742c9e0ed)

Adjusted Sub:

![Adjusted](https://github.com/user-attachments/assets/30a422b8-e8f1-4351-a632-01f6c41efbad)

Example 3 Original Sub:

![Original](https://github.com/user-attachments/assets/abcb7e51-974e-4cf8-8ba4-0310459c13ed)

Adjusted Sub with scene change:

![Adjusted](https://github.com/user-attachments/assets/b2fc1fa4-83c5-4b2e-9596-63e3d9408b57)

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
