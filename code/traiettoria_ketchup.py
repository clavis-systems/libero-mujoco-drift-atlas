#!/usr/bin/env python3
"""Traiettoria verticale del ketchup in libero_10 (task 0, 1, 7), passo per passo (aggiunta dopo la revisione di Codex).

Due modi:

  misura   (dentro l'ambiente di una versione) registra, per ogni stato, quota z e velocità del ketchup a ogni passo da 0 a
           100 dopo set_init_state (stessa sequenza e stessi semi di atlante_deriva.py) e i contatti del ketchup allo
           stato salvato (con chi e con quale distanza: distanza negativa = compenetrazione):
             ~/deriva/venv-3.8.1/bin/python -I traiettoria_ketchup.py misura --out DIR [--task 0 1 7]

  tabella  (senza dipendenze) legge i JSON di due o più versioni e scrive il testo leggibile:
             python traiettoria_ketchup.py tabella --dati DIR --out traiettoria_ketchup.txt

Serve a rendere verificabili, senza aprire i .npz, le frasi della NOTA sul ketchup ("picco a 1,08 m", "ancora in volo
al passo 10", causa del lancio).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

QUI = Path(__file__).resolve().parent
PASSI_TABELLA = list(range(0, 11)) + [20, 40, 100]


def _carica_ad():
    spec = importlib.util.spec_from_file_location("atlante_deriva", QUI / "atlante_deriva.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def contatti_ketchup(env, voce_ketchup):
    """Contatti del corpo del ketchup allo stato salvato: lista (altro corpo, distanza in m)."""
    import mujoco

    ad = _carica_ad()
    m, d = ad._modello_dati(env)
    giunto = [j for j in range(m.njnt) if int(m.jnt_qposadr[j]) == voce_ketchup[2]][0]
    corpo = int(m.jnt_bodyid[giunto])
    out = []
    for k in range(d.ncon):
        c = d.contact[k]
        b1, b2 = int(m.geom_bodyid[c.geom1]), int(m.geom_bodyid[c.geom2])
        if corpo in (b1, b2):
            altro = b2 if b1 == corpo else b1
            out.append((mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, altro) or f"corpo{altro}", float(c.dist)))
    return out


def misura(args) -> int:
    import numpy as np
    import mujoco
    import libero.libero as L

    ad = _carica_ad()
    radice = Path(L.__file__).resolve().parent
    nomi = ad.elenco_task(radice, "libero_10")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for t in args.task:
        t0 = time.time()
        stati = ad.carica_stati(Path(L.get_libero_path("init_states")) / "libero_10" / f"{nomi[t]}.pruned_init")
        env = ad.crea_env(str(Path(L.get_libero_path("bddl_files")) / "libero_10" / f"{nomi[t]}.bddl"))
        try:
            env.seed(0)
            env.reset()
            voci = ad.voci_oggetti(env)
            k = [i for i, v in enumerate(voci) if v[1] == 0 and "ketchup" in v[0]]
            assert len(k) == 1, f"attesa una sola voce libera 'ketchup', trovate {len(k)}"
            k = k[0]
            adr, adr_dof = voci[k][2], voci[k][3]
            z = np.zeros((len(stati), 101))
            v = np.zeros((len(stati), 101))
            contatti = []
            for i, stato in enumerate(stati):
                env.seed(i)
                env.reset()
                env.set_init_state(stato)
                _, d = ad._modello_dati(env)  # il reset rigido ricrea la simulazione: i dati vanno riletti ogni volta
                z[i, 0] = d.qpos[adr + 2]
                v[i, 0] = float(np.linalg.norm(d.qvel[adr_dof : adr_dof + 3]))
                contatti.append(contatti_ketchup(env, voci[k]))
                for passo in range(1, 101):
                    env.step(ad.AZIONE_NULLA)
                    z[i, passo] = d.qpos[adr + 2]
                    v[i, passo] = float(np.linalg.norm(d.qvel[adr_dof : adr_dof + 3]))
        finally:
            env.close()
        res = {"mujoco": mujoco.__version__, "task": t, "nome": nomi[t], "voce": voci[k][0], "n_stati": len(stati),
               "z": z.tolist(), "velocita": v.tolist(), "contatti_stato_salvato": contatti}
        (out / f"m{mujoco.__version__}_t{t}.json").write_text(json.dumps(res), encoding="utf-8")
        print(f"[{mujoco.__version__}] traiettoria ketchup libero_10 task {t}: {len(stati)} stati, {round(time.time()-t0, 1)} s", flush=True)
    return 0


def _med(xs):
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])


def tabella(args) -> int:
    dati = Path(args.dati)
    righe = ["TRAIETTORIA VERTICALE DEL KETCHUP (libero_10) — quota z in metri e velocità lineare in m/s, mediana (minimo..massimo) sui 50 stati.",
             "Passo 0 = subito dopo set_init_state (stato salvato). Generato da traiettoria_ketchup.py; dati grezzi nei JSON accanto.\n"]
    for t in (0, 1, 7):
        per_v = {}
        for f in sorted(dati.glob(f"m*_t{t}.json")):
            r = json.loads(f.read_text(encoding="utf-8"))
            per_v[r["mujoco"]] = r
        if not per_v:
            continue
        nome = next(iter(per_v.values()))["nome"]
        righe.append(f"=== libero_10 task {t}: {nome}")
        for ver, r in per_v.items():
            z, v = r["z"], r["velocita"]
            n = r["n_stati"]
            picchi = [max(z[i]) for i in range(n)]
            passo_picco = [z[i].index(max(z[i])) for i in range(n)]
            righe.append(f"-- MuJoCo {ver} (oggetto: {r['voce']}); quota salvata mediana {_med([z[i][0] for i in range(n)]):.4f} m")
            righe.append(f"   picco di quota: mediana {_med(picchi):.4f} m (min {min(picchi):.4f}, max {max(picchi):.4f}), al passo {int(_med(passo_picco))} (mediana)")
            righe.append("   passo | z mediana (min..max)        | velocità mediana (max)   | z stato 0")
            for p in PASSI_TABELLA:
                zp = [z[i][p] for i in range(n)]
                vp = [v[i][p] for i in range(n)]
                righe.append(f"   {p:5d} | {_med(zp):.4f} ({min(zp):.4f}..{max(zp):.4f}) | {_med(vp):.4g} ({max(vp):.4g}) | {z[0][p]:.4f}")
            in_volo = sum(1 for i in range(n) if v[i][10] > 0.05)
            righe.append(f"   stati con velocità > 0,05 m/s al passo 10: {in_volo}/{n}; al passo 100: {sum(1 for i in range(n) if v[i][100] > 0.05)}/{n}")
            # contatti allo stato salvato
            cont = r["contatti_stato_salvato"]
            con_pen = [c for c in cont if any(d < -1e-4 for _, d in c)]
            if con_pen:
                esempio = sorted(con_pen[0], key=lambda x: x[1])[:3]
                righe.append(f"   contatti allo stato salvato: {len(con_pen)}/{n} stati con compenetrazione > 0,1 mm; stato 0 (peggiori): "
                             + ", ".join(f"{a} {d*100:.2f} cm" for a, d in esempio))
            else:
                righe.append(f"   contatti allo stato salvato: nessuna compenetrazione > 0,1 mm in {n} stati (contatti totali stato 0: {len(cont[0])})")
        righe.append("")
    Path(args.out).write_text("\n".join(righe) + "\n", encoding="utf-8")
    print("\n".join(righe))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("misura")
    a.add_argument("--out", required=True)
    a.add_argument("--task", type=int, nargs="+", default=[0, 1, 7])
    b = sub.add_parser("tabella")
    b.add_argument("--dati", required=True)
    b.add_argument("--out", required=True)
    args = ap.parse_args()
    return misura(args) if args.cmd == "misura" else tabella(args)


if __name__ == "__main__":
    sys.exit(main())
