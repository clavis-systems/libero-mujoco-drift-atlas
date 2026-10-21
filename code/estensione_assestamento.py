#!/usr/bin/env python3
"""ESTENSIONE POST-HOC (non prevista nella PREMESSA): prosegue l'assestamento oltre i 10 passi.

Dopo aver visto che in libero_10 (task 0, 1, 7) il ketchup è ancora in volo al passo 10 (velocità non nulla), questa
estensione registra lo stato a 10, 20, 40 e 100 passi per i task colpiti, per capire se lo scarto fra versioni è un
transitorio o resta a riposo. Non cambia soglie né classi dell'atlante: serve solo a interpretare i risultati.

    ~/deriva/venv-3.8.1/bin/python -I estensione_assestamento.py --suite libero_10 --task 0 1 7 --out ~/deriva/dati/estensione/m3.8.1

Riusa la stessa sequenza di atlante_deriva.py (stessi semi: stato i usa seme i).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np

QUI = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("atlante_deriva", QUI / "atlante_deriva.py")
ad = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ad)

PASSI_REGISTRATI = (10, 20, 40, 100)


def misura_task_esteso(bddl: str, stati: np.ndarray):
    env = ad.crea_env(bddl)
    try:
        env.seed(0)
        env.reset()
        voci = ad.voci_oggetti(env)
        q = {p: np.zeros((len(stati), len(voci), 7)) for p in PASSI_REGISTRATI}
        vmax = {p: np.zeros(len(stati)) for p in PASSI_REGISTRATI}
        for i, stato in enumerate(stati):
            env.seed(i)
            env.reset()
            env.set_init_state(stato)
            for passo in range(1, max(PASSI_REGISTRATI) + 1):
                env.step(ad.AZIONE_NULLA)
                if passo in q:
                    q[passo][i] = ad.istantanea(env, voci)
                    vmax[passo][i] = ad.velocita_massima(env, voci)
        return voci, q, vmax
    finally:
        env.close()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--suite", required=True, choices=ad.SUITES)
    ap.add_argument("--task", type=int, nargs="+", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    import mujoco
    import libero.libero as libero_pkg

    radice = Path(libero_pkg.__file__).resolve().parent
    nomi = ad.elenco_task(radice, args.suite)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for t in args.task:
        t0 = time.time()
        stati = ad.carica_stati(Path(libero_pkg.get_libero_path("init_states")) / args.suite / f"{nomi[t]}.pruned_init")
        voci, q, vmax = misura_task_esteso(str(Path(libero_pkg.get_libero_path("bddl_files")) / args.suite / f"{nomi[t]}.bddl"), stati)
        np.savez_compressed(
            out / f"{args.suite}_t{t}.npz",
            **{f"q{p}": q[p] for p in PASSI_REGISTRATI}, **{f"vmax{p}": vmax[p] for p in PASSI_REGISTRATI},
            nomi=np.array([v[0] for v in voci]), tipi=np.array([v[1] for v in voci]),
        )
        print(f"[{mujoco.__version__}] estensione {args.suite} task {t}: {len(stati)} stati, {round(time.time()-t0, 1)} s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
