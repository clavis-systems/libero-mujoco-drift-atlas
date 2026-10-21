# Aggiunta: MuJoCo 3.12.0 (soglie e classi invariate; riferimento 3.3.7; confronto anche con 3.8.1)

Stati iniziali identici a 3.3.7 (verificato, altrimenti il confronto si ferma): 40 task con la stessa impronta del file, 2000 stati salvati identici a bit.


## libero_spatial

| task | A 3.12.0 | vs 3.3.7: stati ≥1 cm | max cm | classe | vs 3.8.1: stati ≥1 cm | max cm | stati ≥1 mm | identici a bit |
|---|---|---|---|---|---|---|---|---|
| 0 | 50 | 0 | 0.6736 | ok | 0 | 0.107 | 1 | 0/50 |
| 1 | 50 | 0 | 0.0015 | ok | 0 | 0.0 | 0 | 0/50 |
| 2 | 50 | 2 | 4.6979 | sfiorato | 2 | 2.5826 | 3 | 0/50 |
| 3 | 50 | 0 | 0.0023 | ok | 0 | 0.0 | 0 | 0/50 |
| 4 | 50 | 0 | 0.3735 | ok | 0 | 0.021 | 0 | 0/50 |
| 5 | 50 | 50 | 4.7796 | COLPITO | 50 | 6.3005 | 50 | 0/50 |
| 6 | 50 | 0 | 0.3398 | ok | 0 | 0.3401 | 50 | 0/50 |
| 7 | 50 | 0 | 0.3398 | ok | 0 | 0.3401 | 50 | 0/50 |
| 8 | 50 | 6 | 6.9714 | COLPITO | 2 | 2.4521 | 2 | 0/50 |
| 9 | 50 | 0 | 0.3398 | ok | 0 | 0.3401 | 50 | 0/50 |

Sintesi libero_spatial: contro 3.3.7 2 COLPITI, 1 sfiorati, 58 stati su 500; contro 3.8.1 54 stati oltre 1 cm.

## libero_object

| task | A 3.12.0 | vs 3.3.7: stati ≥1 cm | max cm | classe | vs 3.8.1: stati ≥1 cm | max cm | stati ≥1 mm | identici a bit |
|---|---|---|---|---|---|---|---|---|
| 0 | 50 | 0 | 0.0001 | ok | 0 | 0.0001 | 0 | 0/50 |
| 1 | 50 | 0 | 0.0001 | ok | 0 | 0.0001 | 0 | 0/50 |
| 2 | 50 | 0 | 0.0001 | ok | 0 | 0.0001 | 0 | 0/50 |
| 3 | 50 | 0 | 0.0001 | ok | 0 | 0.0001 | 0 | 0/50 |
| 4 | 50 | 0 | 0.0001 | ok | 0 | 0.0001 | 0 | 0/50 |
| 5 | 50 | 0 | 0.0 | ok | 0 | 0.0 | 0 | 0/50 |
| 6 | 50 | 0 | 0.0001 | ok | 0 | 0.0001 | 0 | 0/50 |
| 7 | 50 | 0 | 0.0 | ok | 0 | 0.0 | 0 | 0/50 |
| 8 | 50 | 0 | 0.0001 | ok | 0 | 0.0001 | 0 | 0/50 |
| 9 | 50 | 0 | 0.0001 | ok | 0 | 0.0001 | 0 | 0/50 |

Sintesi libero_object: contro 3.3.7 0 COLPITI, 0 sfiorati, 0 stati su 500; contro 3.8.1 0 stati oltre 1 cm.

## libero_goal

| task | A 3.12.0 | vs 3.3.7: stati ≥1 cm | max cm | classe | vs 3.8.1: stati ≥1 cm | max cm | stati ≥1 mm | identici a bit |
|---|---|---|---|---|---|---|---|---|
| 0 | 50 | 0 | 0.0015 | ok | 0 | 0.0 | 0 | 0/50 |
| 1 | 50 | 0 | 0.0015 | ok | 0 | 0.0 | 0 | 0/50 |
| 2 | 50 | 0 | 0.0015 | ok | 0 | 0.0 | 0 | 0/50 |
| 3 | 50 | 0 | 0.0015 | ok | 0 | 0.0 | 0 | 0/50 |
| 4 | 50 | 0 | 0.0015 | ok | 0 | 0.0 | 0 | 0/50 |
| 5 | 50 | 0 | 0.0015 | ok | 0 | 0.0 | 0 | 0/50 |
| 6 | 50 | 0 | 0.0015 | ok | 0 | 0.0 | 0 | 0/50 |
| 7 | 50 | 0 | 0.0015 | ok | 0 | 0.0 | 0 | 0/50 |
| 8 | 50 | 0 | 0.07 | ok | 0 | 0.0012 | 0 | 0/50 |
| 9 | 50 | 0 | 0.0015 | ok | 0 | 0.0 | 0 | 0/50 |

Sintesi libero_goal: contro 3.3.7 0 COLPITI, 0 sfiorati, 0 stati su 500; contro 3.8.1 0 stati oltre 1 cm.

## libero_10

| task | A 3.12.0 | vs 3.3.7: stati ≥1 cm | max cm | classe | vs 3.8.1: stati ≥1 cm | max cm | stati ≥1 mm | identici a bit |
|---|---|---|---|---|---|---|---|---|
| 0 | 50 | 50 | 54.1877 | COLPITO | 0 | 0.0726 | 0 | 0/50 |
| 1 | 50 | 50 | 54.1877 | COLPITO | 0 | 0.0 | 0 | 0/50 |
| 2 | 50 | 0 | 0.0015 | ok | 0 | 0.0 | 0 | 0/50 |
| 3 | 50 | 0 | 0.0015 | ok | 0 | 0.0 | 0 | 0/50 |
| 4 | 50 | 0 | 0.0001 | ok | 0 | 0.0001 | 0 | 0/50 |
| 5 | 50 | 0 | 0.0003 | ok | 0 | 0.0001 | 0 | 0/50 |
| 6 | 50 | 2 | 3.5031 | sfiorato | 1 | 1.4452 | 2 | 0/50 |
| 7 | 50 | 50 | 54.1877 | COLPITO | 0 | 0.0015 | 0 | 0/50 |
| 8 | 0 | 0 | 0.0002 | ok | 0 | 0.0 | 0 | 0/50 |
| 9 | 50 | 0 | 0.0004 | ok | 0 | 0.0 | 0 | 0/50 |

Sintesi libero_10: contro 3.3.7 3 COLPITI, 1 sfiorati, 152 stati su 500; contro 3.8.1 1 stati oltre 1 cm.

## Totali

- 3.12.0 vs_3.3.7: 5 task COLPITI, 2 sfiorati, 210 stati su 2000 oltre 1 cm; scarto massimo 5.419e-01 m.
- 3.12.0 vs_3.8.1: 1 task COLPITI, 3 sfiorati, 55 stati su 2000 oltre 1 cm; scarto massimo 6.301e-02 m.

Sensibilità (3.12.0 contro 3.3.7): 0.1 cm → 379 stati, 9 task COLPITI; 0.5 cm → 215 stati, 5 task COLPITI; 1 cm → 210 stati, 5 task COLPITI; 2 cm → 208 stati, 4 task COLPITI; 5 cm → 151 stati, 3 task COLPITI.

## Oggetti che si spostano ≥ 1 cm rispetto a 3.3.7 (stati contro eventi)

| task | oggetto | stati colpiti | pose distinte (quota+orientazione) su 50 | esiti distinti | scarto max cm |
|---|---|---|---|---|---|
| spatial t2 | akita_black_bowl_2_main | 2 | 1 | 2 | 4.7 |
| spatial t2 | plate_1_main | 2 | 1 | 2 | 3.06 |
| spatial t5 | akita_black_bowl_1_main | 50 | 1 | 1 | 4.78 |
| spatial t8 | akita_black_bowl_1_main | 6 | 1 | 6 | 6.97 |
| spatial t8 | plate_1_main | 1 | 1 | 1 | 1.38 |
| 10 t0 | cream_cheese_1_main | 3 | 1 | 3 | 33.96 |
| 10 t0 | ketchup_1_main | 50 | 1 | 1 | 54.19 |
| 10 t0 | orange_juice_1_main | 50 | 1 | 3 | 38.23 |
| 10 t0 | milk_1_main | 50 | 1 | 2 | 38.23 |
| 10 t1 | ketchup_1_main | 50 | 1 | 1 | 54.19 |
| 10 t1 | orange_juice_1_main | 50 | 1 | 1 | 38.23 |
| 10 t1 | milk_1_main | 50 | 1 | 1 | 38.23 |
| 10 t6 | plate_1_main | 2 | 1 | 2 | 3.5 |
| 10 t7 | tomato_sauce_1_main | 1 | 1 | 1 | 14.65 |
| 10 t7 | ketchup_1_main | 50 | 1 | 1 | 54.19 |

## Controllo nullo di 3.12.0 (semi 1000+i)

1750/2000 stati identici a bit; pavimento del rumore sulla posizione 1.2596 cm; stati oltre 1 cm per solo rumore: 3.
- libero_spatial t3: 50 stati diversi, massimo 0.0 cm (0 stati ≥ 1 cm)
- libero_spatial t4: 50 stati diversi, massimo 1.2596 cm (3 stati ≥ 1 cm)
- libero_spatial t6: 50 stati diversi, massimo 0.0 cm (0 stati ≥ 1 cm)
- libero_spatial t7: 50 stati diversi, massimo 0.0 cm (0 stati ≥ 1 cm)
- libero_spatial t9: 50 stati diversi, massimo 0.0 cm (0 stati ≥ 1 cm)
Ripetizione con lo stesso seme (3.12.0, solo i task che differivano): libero_spatial t3: 50/50 identici a bit; libero_spatial t4: 50/50 identici a bit; libero_spatial t6: 50/50 identici a bit; libero_spatial t7: 50/50 identici a bit; libero_spatial t9: 50/50 identici a bit.

## Ketchup di libero_10 (stato 0; il percorso è identico in tutti i 50 stati)

| versione | task | picco mediano (m) | passo del picco | z al passo 10 (m) | velocità al passo 10 (m/s) | z al passo 20 | z al passo 100 |
|---|---|---|---|---|---|---|---|
| 3.12.0 | 0 | 1.1396 | 7 | 1.0511 | 1.312 | 0.5092 | 0.5092 |
| 3.12.0 | 1 | 1.1396 | 7 | 1.0511 | 1.312 | 0.5092 | 0.5092 |
| 3.12.0 | 7 | 1.1396 | 7 | 1.0511 | 1.312 | 0.5092 | 0.5092 |
| 3.3.7 | 0 | 0.6491 | 4 | 0.5092 | 0.0 | 0.5092 | 0.5092 |
| 3.3.7 | 1 | 0.6491 | 4 | 0.5092 | 0.0 | 0.5092 | 0.5092 |
| 3.3.7 | 7 | 0.6491 | 4 | 0.5092 | 0.0 | 0.5092 | 0.5092 |
| 3.8.1 | 0 | 1.1396 | 7 | 1.0511 | 1.312 | 0.5092 | 0.5092 |
| 3.8.1 | 1 | 1.1396 | 7 | 1.0511 | 1.312 | 0.5092 | 0.5092 |
| 3.8.1 | 7 | 1.1396 | 7 | 1.0511 | 1.312 | 0.5092 | 0.5092 |

Compenetrazione del ketchup nel tavolo allo stato salvato (libero_10 task 0 stato 0): 3.12.0: 2.92 cm, 3.3.7: 1.46 cm, 3.8.1: 2.92 cm.

Ancora `libero_spatial` task 5 (distanza xy ciotola–ramekin dopo l'assestamento, media sui 50 stati; i valori di lerobot#4390 valgono fino a 3.8.1; per 3.12.0 è un dato, non un cancello): 3.3.7: 1.45 cm (min 1.45, max 1.45); 3.8.1: 3.72 cm (min 3.72, max 3.72); 3.12.0: 6.23 cm (min 6.23, max 6.23).

Task in cui 3.12.0 differisce da 3.8.1 di almeno 1 mm in (quasi) tutti i 50 stati, con l'oggetto che si sposta di più (mediana): spatial t5: akita_black_bowl_1_main (6.30 cm) in 50 stati; spatial t6: akita_black_bowl_2_main (0.34 cm) in 50 stati; spatial t7: akita_black_bowl_1_main (0.34 cm) in 50 stati; spatial t9: akita_black_bowl_2_main (0.34 cm) in 50 stati.

## Previsioni dell'aggiunta, verificate

- Q1 (3.12.0 e 3.8.1 entro 1 mm in ≥90% degli stati di almeno 35 task): 36 task su 40 → vera.
- Q2 (3.12.0 non torna a 3.3.7: spatial/5 e libero_10 0, 1, 7 COLPITI): {'libero_spatial t5': 'COLPITO', 'libero_10 t0': 'COLPITO', 'libero_10 t1': 'COLPITO', 'libero_10 t7': 'COLPITO'} → vera.
- Q3 (nessun task di libero_goal COLPITO): colpiti 0, stati oltre soglia 0 → vera.
- Q4 (picco del ketchup sopra 0,8 m): [1.1396, 1.1396, 1.1396] → vera.
- Q5 (profondità del ketchup come 3.8.1, 2,92 cm entro il 5%): 3.12.0 -2.92 cm (3.8.1 -2.92, 3.3.7 -1.46) → vera.
