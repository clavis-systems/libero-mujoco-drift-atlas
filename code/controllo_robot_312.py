#!/usr/bin/env python3
"""Controllo di neutralità delle due patch a robosuite per MuJoCo 3.12.0 (aggiunta del 21/10/2026).

robosuite 1.4.0 non gira su MuJoCo 3.12.0 senza due modifiche di compatibilità (vedi robosuite_mujoco312.patch):
  1. `joint_type in (enum, enum)` fallisce perché in 3.12.0 `enum == np.int32` è falso (l'inverso è vero);
  2. `mj_fullM(m, dst, qM)` è diventata `mj_fullM(m, d, dst)` e `MjData.qM` si chiama `M`.
Nessuna delle due dovrebbe cambiare la fisica. Questo script lo controlla: stessa sequenza di reset di atlante_deriva.py
su uno stato di un task senza compenetrazioni (libero_goal task 0, stato 0), poi stampa la posizione dei 7 giunti del braccio e
delle dita (qpos) e la loro velocità dopo 0, 5 e 10 passi. Si lancia in due ambienti (3.8.1 e 3.12.0) e si confrontano le uscite.

    ~/deriva/venv-3.12.0/bin/python -I controllo_robot_312.py > robot_3.12.0.txt
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("atlante_deriva", QUI / "atlante_deriva.py")
ad = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ad)


def main() -> int:
    import mujoco
    import numpy as np
    import libero.libero as L

    radice = Path(L.__file__).resolve().parent
    nomi = ad.elenco_task(radice, "libero_goal")
    stati = ad.carica_stati(Path(L.get_libero_path("init_states")) / "libero_goal" / f"{nomi[0]}.pruned_init")
    env = ad.crea_env(str(Path(L.get_libero_path("bddl_files")) / "libero_goal" / f"{nomi[0]}.bddl"))
    try:
        env.seed(0)
        env.reset()
        env.set_init_state(stati[0])
        m, d = ad._modello_dati(env)
        robot = [j for j in range(m.njnt)
                 if (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, j) or "").startswith(("robot", "gripper"))]
        print(f"MuJoCo {mujoco.__version__}: libero_goal task 0 stato 0, giunti del robot: {len(robot)}")
        for passo in range(0, 11):
            if passo > 0:
                env.step(ad.AZIONE_NULLA)
            if passo in (0, 5, 10):
                _, d = ad._modello_dati(env)
                q = np.array([d.qpos[int(m.jnt_qposadr[j])] for j in robot])
                v = np.array([d.qvel[int(m.jnt_dofadr[j])] for j in robot])
                print(f"passo {passo:2d} qpos:", " ".join(f"{x:.12f}" for x in q))
                print(f"passo {passo:2d} qvel:", " ".join(f"{x:.9f}" for x in v))
    finally:
        env.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
