# Automatic-Timing-Sub-Fix

REQUISITI FASE 1
- I SUB CHE STAI PER CARICARE NON DEVONO AVERE CARTELLI.
- Carica un .ass o un .srt per la separazione di righe con allineamento in alto sullo schermo e le righe che non lo sono. 
- Quando avrà finito, l'unico file che ti serve è "Sub.srt" che dovrà essere ricaricato nel prossimo script.
(Per non avere troppi file in giro, salvati solo i file in locale "On Top" e "Sub", poi cancella tutto)



REQUISITI FASE 2
- IL PARLATO DEVE ESSERE ALMENO DENTRO LE RIGHE E NON MEZZO FUORI DALLA RIGA (Spettro audio). 
QUINDI NON DEVE ESSERCI L'INIZIO DEL PARLATO CHE INIZIA PRIMA DELLA RIGA, AD ESEMPIO.
BASTA ANCHE UN SYNC ALLA VELOCE UGUALE PER TUTTE LE RIGHE.

- CARICA L'AUDIO DELL'EPISODIO QUI: https://huggingface.co/spaces/abidlabs/music-separation
E SCARICA SOLO I "VOCALI"
QUINDI RINOMINA L'AUDIO APPENA SCARICATO IN "Vocali".wav

- Con la Fase 2 dovrai caricare PRIMA l'audio dell'ep con solo i "vocali" (controlla i requisiti) e poi il file "Sub.srt" della Fase 1.

- Una volta che la Fase 2 sarà completata,  puoi cancellare "temp.wav" e "Sub.srt" della Fase 1.

- Mentre "Vocali" e "adjusted_Sub.srt" non cancellarli da colab.



REQUISITI FASE 3
- Carica il video rinominato in "Ep".mkv su colab (su colab perché ci mette di meno a caricarlo che tramite script).

(Se è un video di piccole dimensioni ancora meglio, ci mette di meno a caricarlo, ma non ridurre troppo la qualità).

- Qundo la Fase 3 sarà finita, avrai due output, "scene-timestamps.srt" (che puoi anche cancellare) e "scene_timestamps_adjusted.srt" che devi tenere caricato su colab.
Puoi anche cancellare "Ep.mkv" che non serve più.



FASE 4

Se avrai seguito le indicazioni precedenti, ti ritroverai alla fine un file "Final.srt".
