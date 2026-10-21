# Aggiunta alla premessa: MuJoCo 3.12.0 (21/10/2026, 16:35, scritta prima di misurare)

`PREMESSA.md` resta com'è (il suo SHA-256 è registrato nei risultati). Questa è un'aggiunta datata, in un file a parte,
scritta **prima** di scaricare e misurare la versione nuova.

## Perché

Dopo aver chiuso l'atlante su 3.3.7, 3.4.0 e 3.8.1 è emerso che il collider box-box di MuJoCo è stato riscritto in
**3.12.0** (rilasciata il 20/08/2026; lo dice il maintainer in
[google-deepmind/mujoco#3476](https://github.com/google-deepmind/mujoco/issues/3476); letto tramite un riassunto
automatico della pagina). Il cambio di 3.4.0 che ha prodotto l'atlante riguardava proprio il box-box (distanza di
compenetrazione riportata esattamente doppia). Chi aggiorna oltre 3.8.1 potrebbe trovare un terzo comportamento. L'utente
ha approvato la misura (21/10). `hf-libero==0.1.4` permette solo `mujoco<3.9`, quindi 3.12 è fuori dal pin ufficiale: si
misura per capire che cosa succede a chi toglie il pin.

## Che cosa si misura

- **Versione:** `mujoco==3.12.0` (unica 3.12.x esistente; ruota `cp312 manylinux x86_64`, 19,8 MB). Gli altri pacchetti sono
  quelli di 3.8.1, già nella cache (stesso `COMUNI` di `prepara_ambiente.sh`). Se servissero pacchetti diversi, mi fermo e chiedo.
- **Codice invariato**, byte per byte, lo stesso che ha prodotto i risultati su 3.3.7, 3.4.0 e 3.8.1
  (`atlante_deriva.py`, `lancia_misura.sh`). Stessi 40 task × 50 stati, stessa sequenza di reset, stessi semi.
- **Stessa soglia (1 cm) e stesse classi** (COLPITO ≥ 5 stati su 50, sfiorato 1–4). Riferimento = **3.3.7**; confronto
  aggiuntivo con **3.8.1** (la versione più recente già misurata).
- **Controlli:** (1) stesso stato iniziale: impronta SHA-256 del file `.pruned_init` e stato salvato `q0` identici a bit a
  quelli di 3.3.7; (2) controllo nullo di 3.12.0 con semi diversi (1000+i), su tutti i 2000 stati, per avere il
  pavimento del rumore di *questa* versione; se un task differisce, ripetizione a stesso seme di quel task;
  (3) `spatial/5` riportata come ancora (1,45 e 3,72 cm valgono per ≤ 3.8.1): per 3.12 **non è un cancello**, è un dato.
- **In più, solo per descrivere:** traiettoria del ketchup in `libero_10` task 0, 1, 7 e compenetrazioni allo stato
  salvato (come per le altre versioni).
- Le soglie e le classi **non** si cambiano dopo aver visto i dati. Il codice di confronto per 3.12 è un file nuovo
  (`confronta_aggiunta.py`), perché `confronta_atlante.py` non cambia.

## Previsioni, scritte prima (deboli)

- **Q1.** 3.12.0 e 3.8.1 danno lo stesso stato assestato (scarto sotto 1 mm) in almeno il 90% degli stati di almeno
  35 task su 40. Le riscritture correggono casi limite, di solito lasciano il caso normale. Fiducia circa 60%.
- **Q2.** 3.12.0 **non** torna al comportamento di 3.3.7: contro 3.3.7 i task COLPITI comprendono ancora `spatial/5` e
  `libero_10` 0, 1, 7. Fiducia circa 70%.
- **Q3.** `libero_goal` non ha task COLPITI con 3.12.0. Fiducia circa 70%.
- **Q4.** Il ketchup di `libero_10` viene ancora espulso dal tavolo: picco di quota sopra 0,8 m con 3.12.0. Fiducia circa 60%.
- **Q5.** La profondità di compenetrazione riportata allo stato salvato per il ketchup è quella di 3.8.1 (2,92 cm, entro
  il 5%). Fiducia circa 55%; ritorno a 1,46 cm circa 20%; un altro valore circa 25%.

## Che cosa non si afferma

Niente sui punteggi di policy; niente su 3.9, 3.10, 3.11 e dalla 3.13 in poi; rendering ancora spento; stessa macchina.
