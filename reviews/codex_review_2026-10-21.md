<!-- Codex's independent read-only review of the atlas, 21 October 2026, copied as received. The only change: links that pointed to local paths on the author's PC now point to the matching files in this repository. The text is in Italian. Findings it raised were closed in a later commit; see README. -->

## 1. Misura e confronti — **PROBLEMA minore: verifiche incomplete**

Il codice registra `q0` subito dopo `set_init_state`, poi `q5` e `q10` dopo i passi previsti; la metrica primaria è il massimo, sugli oggetti liberi, fra distanza xy e scarto z. Le soglie sono in metri (`0.01`) e le tabelle convertono in centimetri; la classe usa almeno 5 stati colpiti, oppure 1–4 sfiorati. Riferimenti: [atlante_deriva.py](../code/atlante_deriva.py:161), [confronta_atlante.py](../code/confronta_atlante.py:54).

Gli indici dei 50 stati e i semi `i` sono gli stessi nelle versioni. Però il confronto **non verifica** che gli hash degli stati iniziali coincidano fra versioni: il codice li registra nei metadati, ma il comparatore non li controlla. Non posso confermare questo punto dai `.npz`, che non ho aperto. Inoltre il codice ignora i giunti sferici (riga 135), assumendo che non siano presenti.

## 2. Cifre, soglie e previsioni — **OK, con una riserva**

La tabella riporta 5 task COLPITI, 2 sfiorati e 209 stati oltre 1 cm; le conte per suite sommano a 57 + 152 = 209. `libero_goal` ha 0/500 oltre soglia e massimo 0,07 cm. Le previsioni P1, P3 e P5 corrispondono ai conteggi; P4 è coerente con i sei task non ok elencati, nessuno in `libero_object`. P2 risulta 40/40: nel CSV i 2.000 scarti posizionali 3.8.1–3.4.0 sono zero alla precisione pubblicata. Riferimenti: [tabella_atlante.md](../results/tabella_atlante.md:66), [atlante_per_stato.csv](../results/atlante_per_stato.csv).

**Riserva:** P2 e l’affermazione “sotto 0,005 cm” si basano su risultati arrotondati; non ho verificato la precisione completa nei `.npz`.

## 3. Ambiente — **OK nei freeze; identità complessiva non provata**

I tre `pip freeze` riportano rispettivamente `mujoco==3.3.7`, `3.4.0`, `3.8.1`. Gli altri 36 pacchetti elencati coincidono. I freeze, da soli, non attestano l’identità di tutto l’ambiente oltre ai pacchetti elencati.

## 4. Affermazioni non sostenute — **PROBLEMA parziale**

Il controllo nullo non è una ripetizione perfetta: solo 1750/2000 stati coincidono a bit; in `spatial/4` due stati differiscono di 1,2512 cm. La NOTA lo dichiara e localizza i due casi; non invalida da solo i 209 conteggi, poiché i task colpiti non sono fra quelli con differenze nel controllo nullo. Riferimento: [tabella_atlante.md](../results/tabella_atlante.md:103).

L’interpretazione del ketchup come **transitorio** è sostenuta: scarto di 54,19 cm a 10 passi, poi mediana 0,65 cm a 20 e 100 passi. Ma quota salvata, picco a 1,08 m, causa del lancio e stato “ancora in volo” non sono verificabili nei risultati testuali leggibili; il possibile contatto iniziale è dichiarato non verificato. L’estensione non comprende il task 1. Riferimenti: NOTA, righe 79–86; tabella, righe 128–131.

**Non controllato:** contenuto dei `.npz`, hash effettivi degli stati iniziali fra versioni e traiettoria verticale dettagliata del ketchup.