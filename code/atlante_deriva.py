#!/usr/bin/env python3
"""Atlante della deriva: misura, per una versione di MuJoCo, quanto si muovono gli oggetti di LIBERO.

Per ogni task di una suite e per ognuno dei 50 stati iniziali ufficiali (file .pruned_init) ripete la sequenza
di reset usata da LeRobot 0.6.1 (`LiberoEnv.reset`):

    env.seed(s); env.reset(); env.set_init_state(stato); 10 passi con l'azione nulla [0,0,0,0,0,0,-1]

e registra lo stato degli oggetti (non del robot) subito dopo `set_init_state` (stato "salvato"), dopo 5 passi e
dopo 10 passi. Niente policy, niente GPU, niente rendering (nessuna fotocamera, nessun contesto OpenGL).

Si lancia dentro l'ambiente della versione da misurare (un ambiente per versione, vedi prepara_ambiente.sh):

    ~/deriva/venv-3.8.1/bin/python atlante_deriva.py --suite libero_goal --out ~/deriva/dati/m3.8.1

Il confronto fra versioni lo fa confronta_atlante.py. Soglie e definizioni sono nella PREMESSA.md.

Sicurezza: i file degli stati iniziali sono pickle (formato torch). Non si usa torch.load: un lettore ristretto
accetta solo gli oggetti numpy necessari e rifiuta tutto il resto.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import pickle
import platform
import sys
import time
import zipfile
import importlib.util
from pathlib import Path

import numpy as np

SUITES = ("libero_spatial", "libero_object", "libero_goal", "libero_10")
N_STATI = 50
PASSI_ATTESA = 10  # num_steps_wait di LeRobot 0.6.1
PASSI_INTERMEDI = 5  # istantanea intermedia (il valore usato da altri valutatori di LIBERO)
FREQ_CONTROLLO = 20  # control_freq di LeRobot 0.6.1
AZIONE_NULLA = [0, 0, 0, 0, 0, 0, -1]  # get_libero_dummy_action()

# tipi di giunto MuJoCo
GIUNTO_LIBERO, GIUNTO_SCORREVOLE, GIUNTO_CERNIERA = 0, 2, 3
CODICE_TIPO = {GIUNTO_LIBERO: 0, GIUNTO_SCORREVOLE: 1, GIUNTO_CERNIERA: 2}  # 0 libero, 1 scorrevole, 2 cerniera


class _LettoreRistretto(pickle.Unpickler):
    """Legge solo array numpy: qualunque altro oggetto nel pickle viene rifiutato."""

    PERMESSI = {
        ("numpy.core.multiarray", "_reconstruct"),
        ("numpy._core.multiarray", "_reconstruct"),
        ("numpy", "ndarray"),
        ("numpy", "dtype"),
        ("_codecs", "encode"),
    }

    def find_class(self, module, name):
        if (module, name) not in self.PERMESSI:
            raise pickle.UnpicklingError(f"oggetto non ammesso nel file degli stati: {module}.{name}")
        if module.startswith("numpy.core"):
            module = module.replace("numpy.core", "numpy._core", 1)
        return super().find_class(module, name)


def carica_stati(percorso: Path) -> np.ndarray:
    with zipfile.ZipFile(percorso) as z:
        nomi = [n for n in z.namelist() if n.endswith("data.pkl")]
        if len(nomi) != 1:
            raise ValueError(f"{percorso}: attesi 1 data.pkl, trovati {len(nomi)}")
        grezzo = z.read(nomi[0])
    arr = _LettoreRistretto(io.BytesIO(grezzo)).load()
    if not isinstance(arr, np.ndarray) or arr.dtype != np.float64 or arr.ndim != 2:
        raise ValueError(f"{percorso}: forma/tipo inattesi: {getattr(arr, 'shape', None)} {getattr(arr, 'dtype', None)}")
    if not np.isfinite(arr).all():
        raise ValueError(f"{percorso}: valori non finiti")
    return arr


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blocco in iter(lambda: f.read(1 << 20), b""):
            h.update(blocco)
    return h.hexdigest()


def elenco_task(radice_libero: Path, suite: str) -> list[str]:
    """Nomi dei task nell'ordine di LeRobot (task_order_index=0, cioè l'identità), senza importare torch."""
    f = radice_libero / "benchmark" / "libero_suite_task_map.py"
    spec = importlib.util.spec_from_file_location("libero_suite_task_map", f)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # file di sole costanti; non si importa il pacchetto benchmark (che importa torch)
    return list(mod.libero_task_map[suite])


def crea_env(bddl: str):
    from libero.libero.envs.env_wrapper import ControlEnv

    return ControlEnv(
        bddl_file_name=bddl,
        use_camera_obs=False,
        has_renderer=False,
        has_offscreen_renderer=False,
        control_freq=FREQ_CONTROLLO,
        hard_reset=True,  # come LeRobot (predefinito): il modello viene ricostruito a ogni reset
    )


def _modello_dati(env):
    sim = env.sim
    m = getattr(sim.model, "_model", None)
    d = getattr(sim.data, "_data", None)
    if m is None or d is None:
        raise RuntimeError("non trovo MjModel/MjData grezzi nel simulatore di robosuite")
    return m, d


def voci_oggetti(env):
    """Elenco dei giunti che non sono del robot: (descrizione, tipo, indirizzo_qpos)."""
    import mujoco

    m, _ = _modello_dati(env)
    voci = []
    for j in range(m.njnt):
        nome_g = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, j) or f"giunto{j}"
        corpo = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, int(m.jnt_bodyid[j])) or f"corpo{int(m.jnt_bodyid[j])}"
        if nome_g.startswith(("robot", "gripper", "mount")) or corpo.startswith(("robot", "gripper", "mount")):
            continue
        tipo = int(m.jnt_type[j])
        if tipo not in CODICE_TIPO:
            continue  # giunti sferici: non presenti nei task
        voci.append((f"{corpo}|{nome_g}", CODICE_TIPO[tipo], int(m.jnt_qposadr[j]), int(m.jnt_dofadr[j])))
    return voci


def istantanea(env, voci) -> np.ndarray:
    """(n_voci, 7): per i giunti liberi x,y,z,qw,qx,qy,qz; per scorrevoli/cerniere il valore nella prima colonna."""
    _, d = _modello_dati(env)
    out = np.zeros((len(voci), 7), dtype=np.float64)
    for k, (_, tipo, adr, _) in enumerate(voci):
        if tipo == 0:
            out[k] = d.qpos[adr : adr + 7]
        else:
            out[k, 0] = d.qpos[adr]
    return out


def velocita_massima(env, voci) -> float:
    _, d = _modello_dati(env)
    v = 0.0
    for _, tipo, _, adr_dof in voci:
        n = 6 if tipo == 0 else 1
        v = max(v, float(np.max(np.abs(d.qvel[adr_dof : adr_dof + n]))))
    return v


def misura_task(bddl: str, stati: np.ndarray, seme_base: int):
    env = crea_env(bddl)
    try:
        env.seed(seme_base)
        env.reset()
        voci = voci_oggetti(env)
        q0 = np.zeros((len(stati), len(voci), 7))
        q5 = np.zeros_like(q0)
        q10 = np.zeros_like(q0)
        vmax = np.zeros(len(stati))
        for i, stato in enumerate(stati):
            env.seed(seme_base + i)
            env.reset()
            if voci_oggetti(env) != voci:  # il modello ricostruito dal reset deve avere gli stessi giunti, nello stesso ordine
                raise RuntimeError(f"{bddl}: i giunti degli oggetti sono cambiati dopo il reset (stato {i})")
            env.set_init_state(stato)
            q0[i] = istantanea(env, voci)
            for passo in range(1, PASSI_ATTESA + 1):
                env.step(AZIONE_NULLA)
                if passo == PASSI_INTERMEDI:
                    q5[i] = istantanea(env, voci)
            q10[i] = istantanea(env, voci)
            vmax[i] = velocita_massima(env, voci)
        return voci, q0, q5, q10, vmax
    finally:
        env.close()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--suite", required=True, choices=SUITES)
    ap.add_argument("--out", required=True, help="cartella di uscita (una per versione)")
    ap.add_argument("--task", type=int, nargs="*", help="solo questi task (per le prove); predefinito: tutti e 10")
    ap.add_argument("--stati", type=int, default=N_STATI, help="quanti stati per task (predefinito 50)")
    ap.add_argument("--seme", type=int, default=0, help="seme base; lo stato i usa seme+i (il controllo nullo usa 1000)")
    args = ap.parse_args()

    import mujoco
    import robosuite
    import libero.libero as libero_pkg

    radice = Path(libero_pkg.__file__).resolve().parent
    cartella_init = Path(libero_pkg.get_libero_path("init_states")) / args.suite
    cartella_bddl = Path(libero_pkg.get_libero_path("bddl_files")) / args.suite
    nomi = elenco_task(radice, args.suite)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    meta = {
        "mujoco": mujoco.__version__,
        "robosuite": robosuite.__version__,
        "numpy": np.__version__,
        "python": sys.version.split()[0],
        "piattaforma": platform.platform(),
        "suite": args.suite,
        "seme_base": args.seme,
        "passi_attesa": PASSI_ATTESA,
        "freq_controllo": FREQ_CONTROLLO,
        "sha256_script": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "task": {},
    }
    ids = args.task if args.task else list(range(len(nomi)))
    for t in ids:
        t0 = time.time()
        f_init = cartella_init / f"{nomi[t]}.pruned_init"
        stati = carica_stati(f_init)[: args.stati]
        voci, q0, q5, q10, vmax = misura_task(str(cartella_bddl / f"{nomi[t]}.bddl"), stati, args.seme)
        np.savez_compressed(
            out / f"{args.suite}_t{t}.npz",
            q0=q0, q5=q5, q10=q10, vmax=vmax,
            nomi=np.array([v[0] for v in voci]), tipi=np.array([v[1] for v in voci]),
        )
        meta["task"][str(t)] = {
            "nome": nomi[t],
            "sha256_init": sha256_file(f_init),
            "n_stati": int(len(stati)),
            "n_voci": len(voci),
            "sha256_q10": hashlib.sha256(q10.tobytes()).hexdigest(),
            "secondi": round(time.time() - t0, 1),
        }
        print(f"[{mujoco.__version__}] {args.suite} task {t} ({nomi[t][:50]}): {len(stati)} stati, "
              f"{len(voci)} voci, {meta['task'][str(t)]['secondi']} s", flush=True)
        (out / f"{args.suite}_meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
