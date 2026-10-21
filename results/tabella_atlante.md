# Atlante della deriva: tabelle

Riferimento: MuJoCo 3.3.7. Soglia: 1 cm sulla posizione (xy o z) di qualunque oggetto libero. Task *COLPITO* se almeno 5 stati su 50 la superano; *sfiorato* se 1–4.

Colonne: **B** = quanti dei 50 stati hanno, dopo l'assestamento, un oggetto spostato ≥ 1 cm fra le due versioni (misura primaria); **A** = quanti stati hanno un oggetto che, fra stato salvato e stato assestato, si muove ≥ 1 cm nella stessa versione (quanto il task si affida all'assestamento); **max** = scarto massimo in cm.


## libero_spatial

| task | istruzione | A 3.3.7 | A 3.8.1 | B 3.4.0 vs 3.3.7 | B 3.8.1 vs 3.3.7 | max cm (3.8.1 vs 3.3.7) | classe (3.8.1) | oggetto che si sposta di più |
|---|---|---|---|---|---|---|---|---|
| 0 | pick up the black bowl between the plate and the ramekin and place it  | 50 | 50 | 0 | 0 | 0.78 | ok | - |
| 1 | pick up the black bowl next to the ramekin and place it on the plate | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 2 | pick up the black bowl from table center and place it on the plate | 50 | 50 | 2 | 2 | 5.4 | sfiorato | - |
| 3 | pick up the black bowl on the cookie box and place it on the plate | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 4 | pick up the black bowl in the top drawer of the wooden cabinet and pla | 50 | 50 | 0 | 0 | 0.37 | ok | - |
| 5 | pick up the black bowl on the ramekin and place it on the plate | 50 | 50 | 50 | 50 | 3.43 | COLPITO | akita_black_bowl_1_main (3.4 cm) |
| 6 | pick up the black bowl next to the cookie box and place it on the plat | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 7 | pick up the black bowl on the stove and place it on the plate | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 8 | pick up the black bowl next to the plate and place it on the plate | 50 | 50 | 5 | 5 | 5.58 | COLPITO | - |
| 9 | pick up the black bowl on the wooden cabinet and place it on the plate | 50 | 50 | 0 | 0 | 0.0 | ok | - |

Sintesi libero_spatial (3.8.1 contro 3.3.7): 2 task colpiti, 1 sfiorati, 57 stati su 500 oltre la soglia.


## libero_object

| task | istruzione | A 3.3.7 | A 3.8.1 | B 3.4.0 vs 3.3.7 | B 3.8.1 vs 3.3.7 | max cm (3.8.1 vs 3.3.7) | classe (3.8.1) | oggetto che si sposta di più |
|---|---|---|---|---|---|---|---|---|
| 0 | pick up the alphabet soup and place it in the basket | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 1 | pick up the cream cheese and place it in the basket | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 2 | pick up the salad dressing and place it in the basket | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 3 | pick up the bbq sauce and place it in the basket | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 4 | pick up the ketchup and place it in the basket | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 5 | pick up the tomato sauce and place it in the basket | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 6 | pick up the butter and place it in the basket | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 7 | pick up the milk and place it in the basket | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 8 | pick up the chocolate pudding and place it in the basket | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 9 | pick up the orange juice and place it in the basket | 50 | 50 | 0 | 0 | 0.0 | ok | - |

Sintesi libero_object (3.8.1 contro 3.3.7): 0 task colpiti, 0 sfiorati, 0 stati su 500 oltre la soglia.


## libero_goal

| task | istruzione | A 3.3.7 | A 3.8.1 | B 3.4.0 vs 3.3.7 | B 3.8.1 vs 3.3.7 | max cm (3.8.1 vs 3.3.7) | classe (3.8.1) | oggetto che si sposta di più |
|---|---|---|---|---|---|---|---|---|
| 0 | open the middle drawer of the cabinet | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 1 | put the bowl on the stove | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 2 | put the wine bottle on top of the cabinet | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 3 | open the top drawer and put the bowl inside | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 4 | put the bowl on top of the cabinet | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 5 | push the plate to the front of the stove | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 6 | put the cream cheese in the bowl | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 7 | turn on the stove | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 8 | put the bowl on the plate | 50 | 50 | 0 | 0 | 0.07 | ok | - |
| 9 | put the wine bottle on the rack | 50 | 50 | 0 | 0 | 0.0 | ok | - |

Sintesi libero_goal (3.8.1 contro 3.3.7): 0 task colpiti, 0 sfiorati, 0 stati su 500 oltre la soglia.


## libero_10

| task | istruzione | A 3.3.7 | A 3.8.1 | B 3.4.0 vs 3.3.7 | B 3.8.1 vs 3.3.7 | max cm (3.8.1 vs 3.3.7) | classe (3.8.1) | oggetto che si sposta di più |
|---|---|---|---|---|---|---|---|---|
| 0 | LIVING ROOM SCENE2 put both the alphabet soup and the tomato sauce in  | 50 | 50 | 50 | 50 | 54.19 | COLPITO | ketchup_1_main (54.2 cm) |
| 1 | LIVING ROOM SCENE2 put both the cream cheese box and the butter in the | 50 | 50 | 50 | 50 | 54.19 | COLPITO | ketchup_1_main (54.2 cm) |
| 2 | KITCHEN SCENE3 turn on the stove and put the moka pot on it | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 3 | KITCHEN SCENE4 put the black bowl in the bottom drawer of the cabinet  | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 4 | LIVING ROOM SCENE5 put the white mug on the left plate and put the yel | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 5 | STUDY SCENE1 pick up the book and place it in the back compartment of  | 50 | 50 | 0 | 0 | 0.0 | ok | - |
| 6 | LIVING ROOM SCENE6 put the white mug on the plate and put the chocolat | 50 | 50 | 2 | 2 | 4.95 | sfiorato | - |
| 7 | LIVING ROOM SCENE1 put both the alphabet soup and the cream cheese box | 50 | 50 | 50 | 50 | 54.19 | COLPITO | ketchup_1_main (54.2 cm) |
| 8 | KITCHEN SCENE8 put both moka pots on the stove | 0 | 0 | 0 | 0 | 0.0 | ok | - |
| 9 | KITCHEN SCENE6 put the yellow and white mug in the microwave and close | 50 | 50 | 0 | 0 | 0.0 | ok | - |

Sintesi libero_10 (3.8.1 contro 3.3.7): 3 task colpiti, 1 sfiorati, 152 stati su 500 oltre la soglia.


## Sensibilità alla soglia (stati oltre soglia, 3.8.1 contro 3.3.7, tutte le suite)

| soglia | stati | task con ≥1 stato | task COLPITI (≥5) |
|---|---|---|---|
| 0.1 cm | 230 | 9 | 7 |
| 0.5 cm | 215 | 8 | 5 |
| 1 cm | 209 | 7 | 5 |
| 2 cm | 206 | 7 | 4 |
| 5 cm | 152 | 5 | 3 |

## Misure secondarie (3.8.1 contro 3.3.7)

Stati con orientazione diversa ≥ 10°: 54. Stati con un cassetto/anta/manopola diverso (≥ 1 cm o ≥ 5°): 0.


## Controlli

Ancora libero_spatial task 5 (distanza xy ciotola–ramekin dopo l'assestamento, media sui 50 stati; valori di Rick0525 in lerobot#4390):

- MuJoCo 3.3.7: 1.45 cm (min 1.45, max 1.45); atteso ≈ 1.45 cm ± 0.5
- MuJoCo 3.4.0: 3.72 cm (min 3.72, max 3.72)
- MuJoCo 3.8.1: 3.72 cm (min 3.72, max 3.72); atteso ≈ 3.72 cm ± 0.5

Stati iniziali identici fra le versioni (verificato, il confronto si ferma altrimenti): 40 task con la stessa impronta SHA-256 del file .pruned_init in 3.3.7, 3.4.0 e 3.8.1; 4000 confronti di stato salvato (q0) a bit, tutti identici.

Controllo nullo (3.3.7 ripetuto con semi 1000+i invece di i): 1750/2000 stati identici a bit. Pavimento del rumore sulla posizione: 1.2512 cm; stati oltre la soglia di 1 cm per solo rumore: 2.
- libero_spatial t3: 50 stati diversi a bit, scarto massimo di posizione 0.0 cm (0 stati ≥ 1 cm), massimo scarto su una componente 1.11e-16
- libero_spatial t4: 50 stati diversi a bit, scarto massimo di posizione 1.2512 cm (2 stati ≥ 1 cm), massimo scarto su una componente 0.0861
- libero_spatial t6: 50 stati diversi a bit, scarto massimo di posizione 0.0 cm (0 stati ≥ 1 cm), massimo scarto su una componente 1.11e-16
- libero_spatial t7: 50 stati diversi a bit, scarto massimo di posizione 0.0 cm (0 stati ≥ 1 cm), massimo scarto su una componente 1.11e-16
- libero_spatial t9: 50 stati diversi a bit, scarto massimo di posizione 0.0 cm (0 stati ≥ 1 cm), massimo scarto su una componente 1.11e-16

Ripetizione con lo stesso seme (3.3.7, solo i task che nel controllo nullo differivano): libero_spatial t3: 50/50 identici a bit; libero_spatial t4: 50/50 identici a bit; libero_spatial t6: 50/50 identici a bit; libero_spatial t7: 50/50 identici a bit; libero_spatial t9: 50/50 identici a bit.

## Previsioni della premessa, verificate

- P1 (spatial/5 colpito in ≥45 stati con 3.4.0 e 3.8.1): 50 e 50 su 50 → vera.
- P2 (3.4.0 e 3.8.1 uguali entro 1 mm in ≥90% degli stati, quasi ovunque): 40 task su 40; scarto massimo di posizione fra 3.4.0 e 3.8.1, a precisione piena: 4.768e-12 m (4.768e-10 cm); massimo scarto su una qualunque componente (posizione, quaternione, giunti): 4.962e-11; stati identici a bit: 59/2000, task con tutti i 50 stati identici a bit: 1/40.
- P3 (≥30 task su 40 né colpiti né sfiorati): 33 su 40 → vera.
- P4 (altri task colpiti più in spatial e libero_10 che in object): task non ok oltre spatial/5 = [('libero_spatial', 2, 'sfiorato'), ('libero_spatial', 8, 'COLPITO'), ('libero_10', 0, 'COLPITO'), ('libero_10', 1, 'COLPITO'), ('libero_10', 6, 'sfiorato'), ('libero_10', 7, 'COLPITO')]; in libero_object: 0.
- P5 (nessun task di libero_goal COLPITO con 3.8.1): colpiti 0, stati oltre soglia 0, scarto massimo 0.07 cm.

## Estensione post-hoc: assestamento prolungato (NON prevista nella premessa)

Stati su 50 con scarto ≥ 1 cm rispetto a 3.3.7 (e mediana dello scarto in cm) dopo 10, 20, 40 e 100 passi; velocità massima mediana degli oggetti (m/s, 3.8.1) a 10 e a 100 passi.

| task | confronto | 10 passi | 20 passi | 40 passi | 100 passi | vmax 3.8.1 @10 / @100 |
|---|---|---|---|---|---|---|
| libero_spatial t8 | 3.4.0 vs 3.3.7 | 5 (med 0.0) | 5 (med 0.0) | 5 (med 0.0) | 5 (med 0.0) | 2.88e-11 / 1.66e-14 |
| libero_spatial t8 | 3.8.1 vs 3.3.7 | 5 (med 0.0) | 5 (med 0.0) | 5 (med 0.0) | 5 (med 0.0) | 2.88e-11 / 1.66e-14 |
| libero_10 t0 | 3.4.0 vs 3.3.7 | 50 (med 54.19) | 3 (med 0.65) | 3 (med 0.65) | 3 (med 0.65) | 1.63 / 5.63e-14 |
| libero_10 t0 | 3.8.1 vs 3.3.7 | 50 (med 54.19) | 3 (med 0.65) | 3 (med 0.65) | 3 (med 0.65) | 1.63 / 5.63e-14 |
| libero_10 t1 | 3.4.0 vs 3.3.7 | 50 (med 54.19) | 0 (med 0.65) | 0 (med 0.65) | 0 (med 0.65) | 1.63 / 5.78e-14 |
| libero_10 t1 | 3.8.1 vs 3.3.7 | 50 (med 54.19) | 0 (med 0.65) | 0 (med 0.65) | 0 (med 0.65) | 1.63 / 5.78e-14 |
| libero_10 t7 | 3.4.0 vs 3.3.7 | 50 (med 54.19) | 1 (med 0.65) | 1 (med 0.65) | 1 (med 0.65) | 1.31 / 5.71e-14 |
| libero_10 t7 | 3.8.1 vs 3.3.7 | 50 (med 54.19) | 1 (med 0.65) | 1 (med 0.65) | 1 (med 0.65) | 1.31 / 5.71e-14 |
