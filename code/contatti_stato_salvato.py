#!/usr/bin/env python3
"""Contatti di tutti gli oggetti allo stato salvato (subito dopo set_init_state), con la profondità di compenetrazione
che il motore riporta (aggiunta dopo la revisione di Codex, per verificare la causa degli spostamenti).

Per ogni stato richiesto elenca, per ogni corpo non del robot, i contatti con distanza negativa oltre 0,1 mm: con chi,
quanto compenetra (cm) e quanti geom coinvolge. Non fa passi di simulazione.

    ~/deriva/venv-3.8.1/bin/python -I contatti_stato_salvato.py --suite libero_10 --task 0 7 --stato 0 3
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from collections import defaultdict
from pathlib import Path

QUI = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("atlante_deriva", QUI / "atlante_deriva.py")
ad = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ad)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--suite", required=True, choices=ad.SUITES)
    ap.add_argument("--task", type=int, nargs="+", required=True)
    ap.add_argument("--stato", type=int, nargs="+", default=[0])
    args = ap.parse_args()

    import mujoco
    import libero.libero as L

    radice = Path(L.__file__).resolve().parent
    nomi = ad.elenco_task(radice, args.suite)
    print(f"MuJoCo {mujoco.__version__} — compenetrazioni allo stato salvato (distanza < -0,1 mm), per corpo")
    for t in args.task:
        stati = ad.carica_stati(Path(L.get_libero_path("init_states")) / args.suite / f"{nomi[t]}.pruned_init")
        env = ad.crea_env(str(Path(L.get_libero_path("bddl_files")) / args.suite / f"{nomi[t]}.bddl"))
        try:
            for i in args.stato:
                env.seed(i)
                env.reset()
                env.set_init_state(stati[i])
                m, d = ad._modello_dati(env)
                pen = defaultdict(list)
                for k in range(d.ncon):
                    c = d.contact[k]
                    if c.dist >= -1e-4:
                        continue
                    b1, b2 = int(m.geom_bodyid[c.geom1]), int(m.geom_bodyid[c.geom2])
                    n1 = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, b1) or f"corpo{b1}"
                    n2 = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, b2) or f"corpo{b2}"
                    if n1.startswith(("robot", "gripper", "mount")) and n2.startswith(("robot", "gripper", "mount")):
                        continue
                    pen[(n1, n2)].append(float(c.dist))
                print(f"-- {args.suite} task {t} stato {i} ({nomi[t][:60]}): {len(pen)} coppie di corpi compenetrate")
                for (n1, n2), ds in sorted(pen.items(), key=lambda x: min(x[1])):
                    print(f"   {n1} ~ {n2}: peggiore {min(ds)*100:.2f} cm, {len(ds)} contatti")
        finally:
            env.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
