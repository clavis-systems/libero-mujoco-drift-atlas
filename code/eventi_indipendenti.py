#!/usr/bin/env python3
"""Stati contro eventi indipendenti (aggiunta dopo la revisione di Codex).

I 50 stati di un task non sono 50 prove indipendenti: spesso l'oggetto che si sposta parte nello stesso modo in tutti
(es. il ketchup di libero_10, la ciotola di spatial/5) e cambiano solo gli altri oggetti. Per ogni task con almeno uno
stato oltre la soglia (3.8.1 contro 3.3.7, posizione ≥ 1 cm, come nell'atlante) e per ogni oggetto responsabile conta:

  (a) configurazioni iniziali DISTINTE dell'oggetto nei 50 stati, a posa salvata completa (posizione xyz entro 1 mm e
      orientazione entro 1°) — la definizione chiesta dalla revisione;
  (b) configurazioni distinte guardando solo quota z e orientazione (xy ignorato): serve quando l'oggetto poggia su un
      piano e la fisica del contatto dipende dalla quota, non da dove sta sul piano (caso del ketchup nel tavolo);
  (c) ESITI distinti: scarti 3.8.1−3.3.7 (vettore xyz) diversi fra loro oltre 1 mm, fra gli stati colpiti. Due stati con lo
      stesso scarto sono lo stesso evento ripetuto.

Uso (solo numpy):  python eventi_indipendenti.py --dati dati_grezzi --out risultati
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

SUITES = ("libero_spatial", "libero_object", "libero_goal", "libero_10")
SOGLIA_POS = 0.01   # come nell'atlante (PREMESSA)
TOL_POS = 0.001     # 1 mm: tolleranza per dire che due pose o due scarti sono "uguali"
TOL_ANGOLO = 1.0    # gradi


def angolo_gradi(q1, q2):
    d = abs(float(np.dot(q1, q2)))
    return float(np.degrees(2 * np.arccos(min(1.0, d))))


def cluster(vettori, uguali):
    """Raggruppamento greedy: restituisce l'elenco dei rappresentanti e l'etichetta di ogni elemento."""
    reps, etichette = [], []
    for v in vettori:
        for k, r in enumerate(reps):
            if uguali(v, r):
                etichette.append(k)
                break
        else:
            reps.append(v)
            etichette.append(len(reps) - 1)
    return reps, etichette


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dati", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    dati, out = Path(args.dati), Path(args.out)

    righe, risultati = [], []
    for suite in SUITES:
        for t in range(10):
            f_ref, f_alt = dati / "m3.3.7" / f"{suite}_t{t}.npz", dati / "m3.8.1" / f"{suite}_t{t}.npz"
            ref, alt = np.load(f_ref), np.load(f_alt)
            tipi, nomi = ref["tipi"], [str(n).split("|")[0] for n in ref["nomi"]]
            n = ref["q10"].shape[0]
            for k in np.where(tipi == 0)[0]:
                d = alt["q10"][:, k, :3] - ref["q10"][:, k, :3]
                mag = np.maximum(np.linalg.norm(d[:, :2], axis=1), np.abs(d[:, 2]))
                colpiti = np.where(mag >= SOGLIA_POS)[0]
                if len(colpiti) == 0:
                    continue
                q0 = ref["q0"][:, k, :]
                # (a) posa salvata completa
                reps_a, et_a = cluster(range(n), lambda i, j: np.linalg.norm(q0[i, :3] - q0[j, :3]) <= TOL_POS and angolo_gradi(q0[i, 3:], q0[j, 3:]) <= TOL_ANGOLO)
                # (b) quota e orientazione
                reps_b, et_b = cluster(range(n), lambda i, j: abs(q0[i, 2] - q0[j, 2]) <= TOL_POS and angolo_gradi(q0[i, 3:], q0[j, 3:]) <= TOL_ANGOLO)
                # (c) esiti distinti fra gli stati colpiti
                reps_c, et_c = cluster(list(colpiti), lambda i, j: np.linalg.norm(d[i] - d[j]) <= TOL_POS)
                configs_a_colpite = sorted({et_a[i] for i in colpiti})
                configs_b_colpite = sorted({et_b[i] for i in colpiti})
                r = {"suite": suite, "task": t, "oggetto": nomi[k], "stati_colpiti": int(len(colpiti)), "stati_totali": n,
                     "configurazioni_distinte_a_posa_completa_su_50": len(reps_a),
                     "configurazioni_a_posa_completa_fra_i_colpiti": len(configs_a_colpite),
                     "configurazioni_distinte_quota_e_orientazione_su_50": len(reps_b),
                     "configurazioni_quota_e_orientazione_fra_i_colpiti": len(configs_b_colpite),
                     "esiti_distinti_fra_i_colpiti": len(reps_c),
                     "scarto_cm_per_esito": sorted(round(float(max(np.linalg.norm(d[i][:2]), abs(d[i][2]))) * 100, 2) for i in [colpiti[list(et_c).index(e)] for e in range(len(reps_c))])}
                risultati.append(r)
    (out / "eventi_indipendenti.json").write_text(json.dumps(risultati, indent=1, ensure_ascii=False), encoding="utf-8")

    righe.append("# Stati contro eventi indipendenti (3.8.1 contro 3.3.7; la colonna 3.4.0 è identica)\n")
    righe.append("Per ogni oggetto che si sposta di almeno 1 cm in almeno uno stato. Tolleranze: posizione 1 mm, orientazione 1°.\n")
    righe.append("| task | oggetto | stati colpiti | (a) pose iniziali distinte su 50 (posa completa) | (a) fra i colpiti | (b) distinte su 50 (solo z e orientazione) | (b) fra i colpiti | (c) esiti distinti | scarti (cm) |")
    righe.append("|---|---|---|---|---|---|---|---|---|")
    for r in risultati:
        righe.append(f"| {r['suite'].replace('libero_', '')} t{r['task']} | {r['oggetto']} | {r['stati_colpiti']} | {r['configurazioni_distinte_a_posa_completa_su_50']} | "
                     f"{r['configurazioni_a_posa_completa_fra_i_colpiti']} | {r['configurazioni_distinte_quota_e_orientazione_su_50']} | "
                     f"{r['configurazioni_quota_e_orientazione_fra_i_colpiti']} | {r['esiti_distinti_fra_i_colpiti']} | {r['scarto_cm_per_esito']} |")
    tot_stati = sum(r["stati_colpiti"] for r in risultati)
    righe.append(f"\nSomma delle righe: {tot_stati} (oggetto × stato) colpiti; gli stati colpiti nell'atlante sono 209 (uno stato può contare più oggetti).")
    righe.append(f"Esiti distinti, sommati su tutte le righe: {sum(r['esiti_distinti_fra_i_colpiti'] for r in risultati)}.")
    (out / "eventi_indipendenti.md").write_text("\n".join(righe) + "\n", encoding="utf-8")
    print("\n".join(righe))
    return 0


if __name__ == "__main__":
    sys.exit(main())
