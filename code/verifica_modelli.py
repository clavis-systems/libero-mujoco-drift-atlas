#!/usr/bin/env python3
"""Verifica (con asserzione) che nei 40 modelli LIBERO non ci siano giunti sferici fra i giunti degli oggetti.

atlante_deriva.py registra solo giunti liberi, scorrevoli e a cerniera e IGNORA i giunti sferici: se ce ne fossero, lo
stato di quegli oggetti sarebbe sfuggito all'atlante. Questo script costruisce ogni modello (nessun passo di simulazione)
e conta i giunti non del robot per tipo; si ferma con un errore se ne trova uno sferico. Aggiunto dopo la revisione di Codex.

    ~/deriva/venv-3.8.1/bin/python -I verifica_modelli.py > verifica_modelli_3.8.1.txt
"""
from __future__ import annotations

import importlib.util
import sys
from collections import Counter
from pathlib import Path

QUI = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("atlante_deriva", QUI / "atlante_deriva.py")
ad = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ad)

NOMI_TIPO = {0: "libero", 1: "SFERICO", 2: "scorrevole", 3: "cerniera"}


def main() -> int:
    import mujoco
    import libero.libero as L

    radice = Path(L.__file__).resolve().parent
    totale = Counter()
    print(f"MuJoCo {mujoco.__version__}: giunti degli oggetti (non robot) per tipo, in ogni task")
    for suite in ad.SUITES:
        nomi = ad.elenco_task(radice, suite)
        for t, nome in enumerate(nomi):
            env = ad.crea_env(str(Path(L.get_libero_path("bddl_files")) / suite / f"{nome}.bddl"))
            try:
                env.seed(0)
                env.reset()
                m, _ = ad._modello_dati(env)
                conta = Counter()
                for j in range(m.njnt):
                    nome_g = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, j) or f"giunto{j}"
                    corpo = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, int(m.jnt_bodyid[j])) or ""
                    if nome_g.startswith(("robot", "gripper", "mount")) or corpo.startswith(("robot", "gripper", "mount")):
                        continue
                    conta[NOMI_TIPO.get(int(m.jnt_type[j]), f"tipo{int(m.jnt_type[j])}")] += 1
                registrati = len(ad.voci_oggetti(env))
                assert conta["SFERICO"] == 0, f"{suite} task {t}: trovati {conta['SFERICO']} giunti sferici"
                assert not [k for k in conta if k.startswith("tipo")], f"{suite} task {t}: tipi di giunto inattesi {dict(conta)}"
                assert sum(conta.values()) == registrati, f"{suite} task {t}: {sum(conta.values())} giunti contro {registrati} registrati"
            finally:
                env.close()
            totale.update(conta)
            print(f"  {suite} t{t}: {dict(conta)}  (registrati dall'atlante: {registrati})")
    print(f"TOTALE sui 40 modelli: {dict(totale)}")
    print("ASSERZIONE SUPERATA: nessun giunto sferico fra gli oggetti; tutti i giunti degli oggetti sono registrati dall'atlante.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
