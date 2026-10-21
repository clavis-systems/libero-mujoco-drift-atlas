# Atlante della deriva — premessa (scritta e committata prima di qualsiasi misura)

Data: 20/10/2026. Passo 0 del piano `strumenti/idee/riproducibilita_smolvla/PIANO.md` (ramo
`claude/procedural-maps-from-objects-ddefb0`). Solo CPU, nessuna policy, nessun rendering, nessuna GPU.

## 1. Domanda

I 4 × 10 task di LIBERO (spatial, object, goal, 10) partono da 50 stati iniziali salvati. Quegli stati sono stati
registrati con vecchie versioni del simulatore e **contano su un assestamento fisico** dentro `reset()` (10 passi con
azione nulla in LeRobot). Se una versione nuova di MuJoCo assesta gli oggetti in modo diverso, "lo stesso task con gli
stessi 50 stati" non è più lo stesso esame.

Domanda: **per quali task e per quanti dei 50 stati lo stato assestato cambia quando si passa da MuJoCo 3.3.7 a 3.4.0
e a 3.8.1?** In particolare per `libero_goal` con 3.8.1, la versione usata dalla Legge 1 (studio
`clavis-systems/slow-robot-brain`): se anche lì gli stati derivano, il README del repository deve dirlo.

## 2. Verifica di novità (20/10/2026, circa 15 minuti, prima di costruire nulla)

Nessun atlante né misura sistematica trovati. Il caso noto riguarda **un solo task**:

- [lerobot#4390](https://github.com/huggingface/lerobot/issues/4390) (aperta): da MuJoCo 3.4.0 la ciotola di
  `libero_spatial` task 5 non si assesta più sul ramekin (deriva xy 1,45 cm con 3.2.7/3.3.0/3.3.7, 3,72 cm con
  3.4.0/3.6.0/3.8.1). Sonda su 50 stati, un solo task; altri 9 task di spatial "invariati entro il rumore" solo come
  esito di valutazioni con policy, non come misura dello stato. Nessuna risposta dei maintainer.
- [lerobot PR #4465](https://github.com/huggingface/lerobot/pull/4465) (aperta): pin `mujoco<3.4`; l'autore scrive di
  non aver rieseguito l'esperimento di assestamento.
- [LIBERO#141](https://github.com/Lifelong-Robot-Learning/LIBERO/issues/141) (aperta, stesso task) e
  [LIBERO#88](https://github.com/Lifelong-Robot-Learning/LIBERO/issues/88) / PR #140 (canale visivo: pavimento più scuro
  da 3.3.3, non posizioni).
- [isospin01/simblame](https://github.com/isospin01/simblame) (Apache-2.0, un commit del 10/10/2026): trova la versione
  che rompe `libero_spatial/5`; validato solo su quel task; la sua roadmap non prevede un censimento di tutti i task.
- [Rick0525/vla-libero-eval](https://github.com/Rick0525/vla-libero-eval): `mj_settle_probe.py` è parametrizzabile per
  suite/task ma scritto per la coppia ciotola–ramekin; risultati solo su spatial.
- [RLinf#1460](https://github.com/RLinf/RLinf/issues/1460) e
  [SimVLA#14](https://github.com/LUOyk1999/SimVLA/issues/14): punteggi di policy per versione (suite intera o media),
  nessuna misura dello stato per task.
- arXiv [2606.04233](https://arxiv.org/abs/2606.04233) (audit di LIBERO e altri): dall'abstract non misura derive
  di stato; non ho letto il testo completo. Meta-World+ ([2505.11289](https://arxiv.org/abs/2505.11289)) e
  [Dexlab#198](https://github.com/huangkiki/Dexlab/issues/198) (divergenza di replay) sono altri problemi.

Limiti della verifica: ricerca su GitHub/web, non su tutto; niente trovato per robosuite, RoboCasa o Meta-World su
questo tema; due preprint non letti per intero. **Se nel frattempo compare un atlante, la novità decade.**

## 3. Definizioni (fissate qui)

**Sequenza di reset** (come `LiberoEnv.reset` di LeRobot 0.6.1, `hard_reset=True`, `control_freq=20`,
`num_steps_wait=10`): `env.seed(s); env.reset(); env.set_init_state(stato_i); 10 × env.step([0,0,0,0,0,0,-1])`.
Senza fotocamere né rendering (la fisica non dipende da essi; vedi limiti).

**Oggetti** = tutti i giunti che non sono del robot (nomi `robot*`, `gripper*`, `mount*`): corpi liberi (posizione e
orientazione) e giunti articolati (cassetti, ante, manopole: scorrevoli e a cerniera).

**Stati registrati:** `q0` subito dopo `set_init_state` (stato salvato), `q5` dopo 5 passi, `q10` dopo 10 passi.

**Deriva A (assestamento, per versione):** scarto di posizione fra `q0` e `q10` nella stessa versione. Dice quanto un
task si affida all'assestamento; non è di per sé un difetto.

**Deriva B (fra versioni, misura primaria):** per ogni stato, `P = max` sugli oggetti liberi di
`max(‖Δxy‖, |Δz|)` fra `q10` della versione V e `q10` della versione di riferimento **3.3.7**. Si confrontano
3.4.0 con 3.3.7 (il confine), 3.8.1 con 3.3.7 (Legge 1) e, come descrizione, 3.8.1 con 3.4.0. Perché 3.3.7: è l'ultima
versione prima del cambio segnalato in #4390 ed è quella a cui porterebbe il pin della PR #4465. **Non è il "vero"
stato originale**: gli stati furono registrati con altre versioni; misuriamo scarti relativi, non correttezza.

## 4. Soglie e classi (fissate prima di vedere i dati)

| Cosa | Soglia |
|---|---|
| Stato "colpito" (B, primaria) | `P ≥ 1,0 cm` |
| Task **COLPITO** | almeno **5 dei 50** stati colpiti (10%) |
| Task **sfiorato** | 1–4 stati colpiti |
| Task ok | 0 stati colpiti |
| Suite "colpita" | almeno un task COLPITO |
| Secondaria: orientazione | scarto ≥ 10° (angolo fra quaternioni) |
| Secondaria: giunti articolati | scorrevoli ≥ 1 cm o cerniere ≥ 5° |
| Sensibilità (solo tabella) | 0,5 / 1 / 2 / 5 cm |

Le misure secondarie e la sensibilità si riportano ma **non** cambiano la classe di un task. Si riporta anche il
risultato a 5 passi invece di 10 (qualche valutatore usa 5).

## 5. Controlli (scritti prima)

1. **Controllo positivo / ancora:** `libero_spatial` task 5. Distanza xy ciotola–ramekin dopo l'assestamento, media sui
   50 stati: attesa ≈ 1,45 cm con 3.3.7 e ≈ 3,72 cm con 3.4.0 e 3.8.1 (valori di Rick0525), tolleranza ± 0,5 cm. Se la
   mia pipeline non li riproduce, **niente altro dell'atlante si legge** finché non si capisce perché.
2. **Controllo nullo:** 3.3.7 ripetuto su tutti i 2000 stati con **semi diversi** (1000+i invece di i). Deve coincidere a
   bit. Se non coincide, il massimo scarto osservato diventa il pavimento del rumore e si riporta.
3. **Conta dei dati:** 4 suite × 10 task × 50 stati × 3 versioni = 6000 reset; ogni lacuna si elenca, non si riempie.

## 6. Previsioni (debolmente sostenute, scritte prima)

- P1: `spatial/5` è COLPITO con 3.4.0 e con 3.8.1 in almeno 45 stati su 50 (già noto: è il controllo positivo).
- P2: 3.4.0 e 3.8.1 danno lo stesso stato assestato (scarto < 1 mm) in almeno il 90% degli stati di quasi tutti i task:
  il cambio è a 3.4.0, non dopo.
- P3: almeno 30 task su 40 non sono né colpiti né sfiorati.
- P4: se esistono altri task colpiti, stanno più in `libero_spatial` e `libero_10` (oggetti appoggiati su altri) che in
  `libero_object`.
- P5 (la meno sicura, circa 60%): nessun task di `libero_goal` è COLPITO con 3.8.1. Se invece lo è, il README di
  `slow-robot-brain` va corretto e il confronto interno della Legge 1 resta valido (stessa versione in tutte le
  condizioni), ma i successi assoluti non sono confrontabili con il paper.

## 7. Cosa NON si afferma

- Nessun effetto sui punteggi di policy: un oggetto spostato di 1 cm può essere irrilevante per un task e
  decisivo per un altro. Questo studio misura stati, non successi.
- Nessuna affermazione su MuJoCo diversi da 3.3.7, 3.4.0, 3.8.1, né su robosuite diverso da 1.4.0.
- Questi 40 task × 50 stati sono l'**intera popolazione** degli stati ufficiali (non un campione): le conte per task si
  leggono come censimento. Una conclusione che richieda di generalizzare oltre questi stati (altre posizioni iniziali)
  non è coperta.

## 8. Limiti noti (dichiarati prima)

- Rendering spento: assumo che la fisica sia identica a quella con fotocamere accese (il rendering non scrive nello
  stato fisico). Non verificato qui: nell'ambiente a CPU non c'è un contesto OpenGL; l'ancora spatial/5 è il controllo
  indiretto.
- Hardware: WSL su CPU locale, Python 3.12; la Legge 1 è girata su Kaggle (CPU/GPU diverse). MuJoCo non è garantito
  identico a bit fra CPU diverse; le soglie di 1 cm sono molto sopra il rumore numerico, salvo contatti caotici (impilamenti
  instabili), che il controllo nullo non copre fra macchine.
- robosuite 1.4.0 e hf-libero 0.1.4 (come la Legge 1); la sonda di Rick0525 usava robosuite 1.4.1.
- Solo le quattro suite da 10 task (non libero_90).

## 9. Ambiente (separato da `~/robotica`) e pacchetti — soggetto all'OK dell'utente

`~/deriva` in WSL Ubuntu, un ambiente `uv` per versione (Python 3.12 già presente come interprete di sola lettura in
`~/.local/share/uv/python`; cache `uv` propria). Versioni uguali al `pip freeze` della fase B della Legge 1 dove
esistono; **senza torch, lerobot, transformers, wandb**. Il codice è letto prima di essere eseguito; i file degli stati
(pickle) si leggono con un lettore ristretto che ammette solo array numpy, non con `torch.load`.

Download: `uv==0.13.4` (17 MB); per ogni ambiente `mujoco` (3.3.7, 3.4.0 o 3.8.1: 7 MB l'uno) e il resto in comune:
`robosuite==1.4.0` (193 MB), `hf-libero==0.1.4` (3 MB), `bddl==1.0.1` (0,2 MB, senza dipendenze), `numpy==2.2.6`,
`scipy==1.18.1`, `numba==0.68.0`, `llvmlite==0.50.0` (60 MB), `pillow==12.3.0`, `opencv-python-headless==4.13.0.92`
(56 MB), `matplotlib==3.11.2` (+ contourpy, cycler, fonttools, kiwisolver, packaging, pyparsing, python-dateutil, six),
`imageio==2.38.1`, `h5py==3.16.0`, `gymnasium==1.4.0` (+ cloudpickle, typing-extensions, farama-notifications),
`easydict`, `pyyaml`, `termcolor`, `tqdm`, `networkx`, `future`, `absl-py`, `etils`, `zipp`, `glfw`, `pyopengl`.
Totale stimato **≈ 450 MB scaricati** (una sola volta, poi riuso dalla cache), circa 2 GB su disco. Gli asset di LIBERO
(409 MB) si **copiano dalla cache locale già scaricata**, nessuna rete.

## 10. Piano di esecuzione

Un processo alla volta (WSL ha 7,5 GB di RAM). Ordine: prova su un solo task → 3.3.7 → 3.8.1 → 3.4.0 → controllo nullo.
Tabelle con `confronta_atlante.py` (che stampa gli hash di questa premessa e del proprio codice). Consegna in
`strumenti/deriva_mujoco/`: questa premessa, gli script, le tabelle e una nota in italiano. Nessuna pubblicazione: la
decide l'utente, che vede prima la lista esatta dei file.

Se dopo questa premessa devo correggere un difetto di codice, lo annoto come commit separato; le soglie e le classi qui
sopra non si cambiano dopo aver visto i dati.
