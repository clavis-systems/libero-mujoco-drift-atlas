#!/usr/bin/env python3
"""Confronta le misure di atlante_deriva.py fra versioni di MuJoCo e scrive le tabelle.

Uso (serve solo numpy):

    python confronta_atlante.py --dati ~/deriva/dati --out strumenti/deriva_mujoco/risultati

La cartella --dati contiene una sottocartella per versione (m3.3.7, m3.4.0, m3.8.1), ognuna con i file
<suite>_t<k>.npz e <suite>_meta.json prodotti da atlante_deriva.py. Se esiste anche <dati>/controllo_nullo/m3.3.7
(stessa versione, semi diversi) viene confrontata con m3.3.7 come controllo nullo.

Soglie e definizioni: PREMESSA.md (fissate prima di misurare). Questo file non contiene scelte nuove.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

SUITES = ("libero_spatial", "libero_object", "libero_goal", "libero_10")
RIFERIMENTO = "3.3.7"
ALTRE = ("3.4.0", "3.8.1")
COPPIE = (("3.4.0", "3.3.7"), ("3.8.1", "3.3.7"), ("3.8.1", "3.4.0"))  # (versione, riferimento)

# --- soglie della PREMESSA (non modificare dopo aver visto i risultati) ---
SOGLIA_POS = 0.01        # 1 cm: scarto di posizione (xy o z) di un oggetto libero
SOGLIA_ANGOLO = 10.0     # gradi: scarto di orientazione (secondario)
SOGLIA_SCORR = 0.01      # 1 cm: scarto di un giunto scorrevole (secondario)
SOGLIA_CERN = 5.0        # gradi: scarto di un giunto a cerniera (secondario)
STATI_COLPITO = 5        # un task è "colpito" se almeno 5 dei 50 stati superano la soglia
SENSIBILITA = (0.001, 0.005, 0.01, 0.02, 0.05)  # solo per la tabella di sensibilità (1 mm serve a verificare P2)
ANCORA_NOTA = {"3.3.7": 1.45, "3.8.1": 3.72}  # cm, issue lerobot#4390 (ciotola-ramekin, spatial/5)
ANCORA_TOLLERANZA = 0.5  # cm


def carica(dati: Path, versione: str, suite: str, t: int):
    f = dati / f"m{versione}" / f"{suite}_t{t}.npz"
    if not f.exists():
        return None
    z = np.load(f, allow_pickle=False)
    return {k: z[k] for k in z.files}


def meta(dati: Path, versione: str, suite: str):
    f = dati / f"m{versione}" / f"{suite}_meta.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def scarti(a: np.ndarray, b: np.ndarray, tipi: np.ndarray):
    """Scarti per stato fra due istantanee (stati, voci, 7). Restituisce metri/gradi/radianti per stato."""
    liberi = tipi == 0
    scorr = tipi == 1
    cern = tipi == 2
    n = a.shape[0]
    pos = np.zeros(n)
    ang = np.zeros(n)
    sc = np.zeros(n)
    ce = np.zeros(n)
    if liberi.any():
        dxy = np.linalg.norm(a[:, liberi, :2] - b[:, liberi, :2], axis=-1)
        dz = np.abs(a[:, liberi, 2] - b[:, liberi, 2])
        pos = np.maximum(dxy, dz).max(axis=1)
        d = np.abs(np.sum(a[:, liberi, 3:7] * b[:, liberi, 3:7], axis=-1))
        ang = np.degrees(2 * np.arccos(np.clip(d, 0.0, 1.0))).max(axis=1)
    if scorr.any():
        sc = np.abs(a[:, scorr, 0] - b[:, scorr, 0]).max(axis=1)
    if cern.any():
        ce = np.degrees(np.abs(a[:, cern, 0] - b[:, cern, 0])).max(axis=1)
    return pos, ang, sc, ce


def per_oggetto(a, b, tipi, nomi):
    """Mediana dello scarto di posizione per ogni oggetto libero (per dire chi si muove)."""
    liberi = np.where(tipi == 0)[0]
    risultati = []
    for k in liberi:
        dxy = np.linalg.norm(a[:, k, :2] - b[:, k, :2], axis=-1)
        dz = np.abs(a[:, k, 2] - b[:, k, 2])
        risultati.append((str(nomi[k]).split("|")[0], float(np.median(np.maximum(dxy, dz)))))
    risultati.sort(key=lambda x: -x[1])
    return risultati


def classe(n_colpiti: int) -> str:
    if n_colpiti >= STATI_COLPITO:
        return "COLPITO"
    return "sfiorato" if n_colpiti >= 1 else "ok"


def distanza_ciotola_ramekin(q: np.ndarray, q0: np.ndarray, tipi: np.ndarray, nomi) -> np.ndarray:
    """Come la sonda di Rick0525: distanza xy fra la ciotola che a t=0 è più vicina al ramekin e il ramekin (m)."""
    nomi = [str(n).split("|")[0] for n in nomi]
    ram = [k for k, n in enumerate(nomi) if "ramekin" in n and tipi[k] == 0]
    bow = [k for k, n in enumerate(nomi) if "bowl" in n and tipi[k] == 0]
    if not ram or not bow:
        return np.full(q.shape[0], np.nan)
    r = ram[0]
    out = np.zeros(q.shape[0])
    for i in range(q.shape[0]):
        d0 = [np.linalg.norm(q0[i, b, :2] - q0[i, r, :2]) for b in bow]
        b = bow[int(np.argmin(d0))]
        out[i] = np.linalg.norm(q[i, b, :2] - q[i, r, :2])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dati", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--premessa", default=str(Path(__file__).with_name("PREMESSA.md")))
    args = ap.parse_args()
    dati, out = Path(args.dati), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    righe_stato = []
    righe_task = []
    riassunto = {"soglie": {"pos_m": SOGLIA_POS, "angolo_gradi": SOGLIA_ANGOLO, "scorrevole_m": SOGLIA_SCORR,
                            "cerniera_gradi": SOGLIA_CERN, "stati_colpito": STATI_COLPITO},
                 "sha256_premessa": hashlib.sha256(Path(args.premessa).read_bytes()).hexdigest() if Path(args.premessa).exists() else None,
                 "sha256_confronta": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 "suite": {}, "ancora_spatial5": {}, "controllo_nullo": None, "mancanti": []}

    verifica = {"task_verificati": 0, "stati_q0_confrontati": 0, "stati_q0_diversi": 0}
    for suite in SUITES:
        riassunto["suite"][suite] = {"task": {}}
        for t in range(10):
            dv = {v: carica(dati, v, suite, t) for v in (RIFERIMENTO,) + ALTRE}
            if any(x is None for x in dv.values()):
                riassunto["mancanti"].append(f"{suite} t{t}: " + ",".join(v for v, x in dv.items() if x is None))
                continue
            nome = (meta(dati, RIFERIMENTO, suite) or {}).get("task", {}).get(str(t), {}).get("nome", f"task{t}")
            ref = dv[RIFERIMENTO]
            tipi, nomi = ref["tipi"], ref["nomi"]
            for v in ALTRE:  # stessa struttura di giunti in tutte le versioni?
                if not (np.array_equal(dv[v]["nomi"], nomi) and np.array_equal(dv[v]["tipi"], tipi)):
                    raise SystemExit(f"{suite} t{t}: i giunti degli oggetti differiscono fra {RIFERIMENTO} e {v}")
            # stessi stati iniziali in tutte le versioni: stessa impronta del file e stesso stato salvato (q0) a bit, stato per stato
            hash_v = {v: ((meta(dati, v, suite) or {}).get("task", {}).get(str(t), {}).get("sha256_init")) for v in (RIFERIMENTO,) + ALTRE}
            if None in hash_v.values() or len(set(hash_v.values())) != 1:
                raise SystemExit(f"{suite} t{t}: impronta del file degli stati iniziali mancante o diversa fra le versioni: {hash_v}")
            verifica["task_verificati"] += 1
            for v in ALTRE:
                diversi = [i for i in range(ref["q0"].shape[0]) if not np.array_equal(ref["q0"][i], dv[v]["q0"][i])]
                if diversi:
                    raise SystemExit(f"{suite} t{t}: lo stato salvato (q0) di {len(diversi)} stati differisce fra {RIFERIMENTO} e {v}; primi: {diversi[:5]}")
                verifica["stati_q0_confrontati"] += ref["q0"].shape[0]
            n = ref["q10"].shape[0]
            rec = {"suite": suite, "task": t, "nome": nome, "n_stati": n, "voci": len(nomi)}
            # A: assestamento per versione (stato salvato -> dopo 10 passi)
            for v, d in dv.items():
                pos, ang, sc, ce = scarti(d["q0"], d["q10"], tipi)
                rec[f"A_{v}_n"] = int((pos >= SOGLIA_POS).sum())
                rec[f"A_{v}_max_cm"] = round(float(pos.max()) * 100, 2)
                rec[f"A_{v}_mediana_cm"] = round(float(np.median(pos)) * 100, 2)
                rec[f"vmax_{v}"] = float(d["vmax"].max())
            # B: scarto fra versioni dello stato assestato (misura primaria)
            for v, r in COPPIE:
                pos, ang, sc, ce = scarti(dv[v]["q10"], dv[r]["q10"], tipi)
                pos5, _, _, _ = scarti(dv[v]["q5"], dv[r]["q5"], tipi)
                k = f"{v}_vs_{r}"
                rec[f"B_{k}_n"] = int((pos >= SOGLIA_POS).sum())
                rec[f"B_{k}_max_cm"] = round(float(pos.max()) * 100, 2)
                rec[f"B_{k}_mediana_cm"] = round(float(np.median(pos)) * 100, 2)
                rec[f"B_{k}_n_5passi"] = int((pos5 >= SOGLIA_POS).sum())
                rec[f"B_{k}_orient_n"] = int((ang >= SOGLIA_ANGOLO).sum())
                rec[f"B_{k}_artic_n"] = int(((sc >= SOGLIA_SCORR) | (ce >= SOGLIA_CERN)).sum())
                for s in SENSIBILITA:
                    rec[f"B_{k}_n_{int(s*1000)}mm"] = int((pos >= s).sum())
                rec[f"B_{k}_classe"] = classe(rec[f"B_{k}_n"])
                if k == "3.8.1_vs_3.4.0":  # precisione piena, senza arrotondamenti (previsione P2)
                    rec["P2_max_pos_m"] = float(pos.max())
                    rec["P2_max_componente"] = float(np.abs(dv[v]["q10"] - dv[r]["q10"]).max())
                    rec["P2_stati_identici_a_bit"] = int(sum(np.array_equal(dv[v]["q10"][i], dv[r]["q10"][i]) for i in range(n)))
                chi = per_oggetto(dv[v]["q10"], dv[r]["q10"], tipi, nomi)
                rec[f"B_{k}_oggetto"] = f"{chi[0][0]} ({chi[0][1]*100:.1f} cm)" if chi and chi[0][1] >= 0.001 else "-"
                for i in range(n):
                    righe_stato.append({"suite": suite, "task": t, "stato": i, "coppia": k,
                                        "scarto_pos_cm": round(float(pos[i]) * 100, 4),
                                        "scarto_orient_gradi": round(float(ang[i]), 3),
                                        "scarto_scorr_cm": round(float(sc[i]) * 100, 4),
                                        "scarto_cerniera_gradi": round(float(ce[i]), 3)})
            righe_task.append(rec)
            riassunto["suite"][suite]["task"][str(t)] = rec
            if suite == "libero_spatial" and t == 5:
                for v, d in dv.items():
                    dist = distanza_ciotola_ramekin(d["q10"], d["q0"], tipi, nomi) * 100
                    riassunto["ancora_spatial5"][v] = {"media_cm": round(float(np.nanmean(dist)), 2),
                                                       "min_cm": round(float(np.nanmin(dist)), 2),
                                                       "max_cm": round(float(np.nanmax(dist)), 2)}

    riassunto["verifica_stati_iniziali"] = verifica

    # controllo nullo: stessa versione, semi diversi, devono coincidere bit a bit
    nullo = dati / "controllo_nullo"
    if (nullo / f"m{RIFERIMENTO}").exists():
        confrontati, uguali_bit, max_pos, max_assoluto, n_ge_soglia = 0, 0, 0.0, 0.0, 0
        per_task = {}
        for suite in SUITES:
            for t in range(10):
                a, b = carica(dati, RIFERIMENTO, suite, t), carica(nullo, RIFERIMENTO, suite, t)
                if a is None or b is None or a["q10"].shape != b["q10"].shape:
                    continue
                if not np.array_equal(a["q0"], b["q0"]):
                    raise SystemExit(f"{suite} t{t}: nel controllo nullo gli stati salvati (q0) non coincidono con la prima esecuzione")
                n = a["q10"].shape[0]
                confrontati += n
                ugu = int(sum(np.array_equal(a["q10"][i], b["q10"][i]) for i in range(n)))
                uguali_bit += ugu
                pos, _, _, _ = scarti(a["q10"], b["q10"], a["tipi"])
                max_pos = max(max_pos, float(pos.max()))
                max_assoluto = max(max_assoluto, float(np.abs(a["q10"] - b["q10"]).max()))
                n_ge_soglia += int((pos >= SOGLIA_POS).sum())
                if ugu < n:
                    per_task[f"{suite} t{t}"] = {"stati_diversi_a_bit": n - ugu, "max_pos_cm": round(float(pos.max()) * 100, 4),
                                                 "stati_pos_ge_1cm": int((pos >= SOGLIA_POS).sum()),
                                                 "max_scarto_componente": float(np.abs(a["q10"] - b["q10"]).max())}
        riassunto["controllo_nullo"] = {"stati_confrontati": confrontati, "stati_identici_a_bit": uguali_bit,
                                        "pavimento_posizione_cm": round(max_pos * 100, 4), "stati_posizione_ge_soglia": n_ge_soglia,
                                        "scarto_massimo_componente": max_assoluto, "task_con_differenze": per_task}

    # ripetizione con lo STESSO seme (solo i task che nel controllo nullo differivano): separa effetto del seme da rumore della macchina
    stesso = dati / "controllo_stesso_seme"
    if (stesso / f"m{RIFERIMENTO}").exists():
        rs = {}
        for suite in SUITES:
            for t in range(10):
                a, b = carica(dati, RIFERIMENTO, suite, t), carica(stesso, RIFERIMENTO, suite, t)
                if a is None or b is None:
                    continue
                n = a["q10"].shape[0]
                rs[f"{suite} t{t}"] = {"stati": n, "identici_a_bit": int(sum(np.array_equal(a["q10"][i], b["q10"][i]) for i in range(n)))}
        riassunto["controllo_stesso_seme"] = rs

    # estensione post-hoc (se presente): stato a 10/20/40/100 passi per alcuni task
    est = dati / "estensione"
    if est.exists():
        estesi = []
        for suite in SUITES:
            for t in range(10):
                dd = {v: carica(est, v, suite, t) for v in (RIFERIMENTO,) + ALTRE}
                if any(x is None for x in dd.values()):
                    continue
                tipi_e = dd[RIFERIMENTO]["tipi"]
                riga = {"suite": suite, "task": t}
                for p in (10, 20, 40, 100):
                    for v, r in COPPIE[:2]:
                        pos, _, _, _ = scarti(dd[v][f"q{p}"], dd[r][f"q{p}"], tipi_e)
                        riga[f"{v}_vs_{r}_p{p}_n"] = int((pos >= SOGLIA_POS).sum())
                        riga[f"{v}_vs_{r}_p{p}_mediana_cm"] = round(float(np.median(pos)) * 100, 2)
                    for v in (RIFERIMENTO,) + ALTRE:
                        riga[f"vmax_{v}_p{p}"] = float(np.median(dd[v][f"vmax{p}"]))
                estesi.append(riga)
        riassunto["estensione_post_hoc"] = estesi

    # verifica automatica delle previsioni della PREMESSA (sezione 6)
    tutti = {(r["suite"], r["task"]): r for r in righe_task}
    prev = {}
    r55 = tutti.get(("libero_spatial", 5))
    if r55:
        prev["P1"] = {"n_3.4.0": r55["B_3.4.0_vs_3.3.7_n"], "n_3.8.1": r55["B_3.8.1_vs_3.3.7_n"],
                      "vera": r55["B_3.4.0_vs_3.3.7_n"] >= 45 and r55["B_3.8.1_vs_3.3.7_n"] >= 45}
    if righe_task:
        ok2 = sum(r["B_3.8.1_vs_3.4.0_n_1mm"] <= 5 for r in righe_task)
        prev["P2"] = {"task_con_90pc_stati_sotto_1mm": ok2, "su": len(righe_task),
                      "max_scarto_cm": max(r["B_3.8.1_vs_3.4.0_max_cm"] for r in righe_task),
                      "max_pos_m_precisione_piena": max(r["P2_max_pos_m"] for r in righe_task),
                      "max_componente_precisione_piena": max(r["P2_max_componente"] for r in righe_task),
                      "stati_identici_a_bit": sum(r["P2_stati_identici_a_bit"] for r in righe_task),
                      "stati_totali": sum(r["n_stati"] for r in righe_task),
                      "task_tutti_identici_a_bit": sum(r["P2_stati_identici_a_bit"] == r["n_stati"] for r in righe_task)}
        puliti = sum(r["B_3.8.1_vs_3.3.7_classe"] == "ok" for r in righe_task)
        prev["P3"] = {"task_ok": puliti, "su": len(righe_task), "vera": puliti >= 30}
        altri = [(r["suite"], r["task"], r["B_3.8.1_vs_3.3.7_classe"]) for r in righe_task
                 if r["B_3.8.1_vs_3.3.7_classe"] != "ok" and not (r["suite"] == "libero_spatial" and r["task"] == 5)]
        prev["P4"] = {"altri_task_non_ok": altri, "in_libero_object": sum(1 for x in altri if x[0] == "libero_object")}
        goal = [r for r in righe_task if r["suite"] == "libero_goal"]
        prev["P5"] = {"libero_goal_task_colpiti": sum(r["B_3.8.1_vs_3.3.7_classe"] == "COLPITO" for r in goal),
                      "libero_goal_stati_oltre_soglia": sum(r["B_3.8.1_vs_3.3.7_n"] for r in goal),
                      "libero_goal_max_cm": max((r["B_3.8.1_vs_3.3.7_max_cm"] for r in goal), default=None)}
    riassunto["previsioni"] = prev

    # --- scritture ---
    with open(out / "atlante_per_stato.csv", "w", newline="", encoding="utf-8") as f:
        if righe_stato:
            w = csv.DictWriter(f, fieldnames=list(righe_stato[0].keys()))
            w.writeheader()
            w.writerows(righe_stato)
    (out / "atlante_riassunto.json").write_text(json.dumps(riassunto, indent=1, ensure_ascii=False), encoding="utf-8")

    L = []
    L.append("# Atlante della deriva: tabelle\n")
    L.append(f"Riferimento: MuJoCo {RIFERIMENTO}. Soglia: {SOGLIA_POS*100:.0f} cm sulla posizione (xy o z) di qualunque oggetto libero. "
             f"Task *COLPITO* se almeno {STATI_COLPITO} stati su 50 la superano; *sfiorato* se 1–{STATI_COLPITO-1}.\n")
    L.append("Colonne: **B** = quanti dei 50 stati hanno, dopo l'assestamento, un oggetto spostato ≥ 1 cm fra le due versioni "
             "(misura primaria); **A** = quanti stati hanno un oggetto che, fra stato salvato e stato assestato, si muove ≥ 1 cm "
             "nella stessa versione (quanto il task si affida all'assestamento); **max** = scarto massimo in cm.\n")
    for suite in SUITES:
        L.append(f"\n## {suite}\n")
        L.append("| task | istruzione | A 3.3.7 | A 3.8.1 | B 3.4.0 vs 3.3.7 | B 3.8.1 vs 3.3.7 | max cm (3.8.1 vs 3.3.7) | classe (3.8.1) | oggetto che si sposta di più |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for r in righe_task:
            if r["suite"] != suite:
                continue
            L.append(f"| {r['task']} | {r['nome'].replace('_', ' ')[:70]} | {r['A_3.3.7_n']} | {r['A_3.8.1_n']} | "
                     f"{r['B_3.4.0_vs_3.3.7_n']} | {r['B_3.8.1_vs_3.3.7_n']} | {r['B_3.8.1_vs_3.3.7_max_cm']} | "
                     f"{r['B_3.8.1_vs_3.3.7_classe']} | {r['B_3.8.1_vs_3.3.7_oggetto']} |")
        rs = [r for r in righe_task if r["suite"] == suite]
        if rs:
            col = sum(r["B_3.8.1_vs_3.3.7_classe"] == "COLPITO" for r in rs)
            sf = sum(r["B_3.8.1_vs_3.3.7_classe"] == "sfiorato" for r in rs)
            tot = sum(r["B_3.8.1_vs_3.3.7_n"] for r in rs)
            L.append(f"\nSintesi {suite} (3.8.1 contro 3.3.7): {col} task colpiti, {sf} sfiorati, {tot} stati su {sum(r['n_stati'] for r in rs)} oltre la soglia.\n")
    L.append("\n## Sensibilità alla soglia (stati oltre soglia, 3.8.1 contro 3.3.7, tutte le suite)\n")
    L.append("| soglia | stati | task con ≥1 stato | task COLPITI (≥5) |")
    L.append("|---|---|---|---|")
    for s in SENSIBILITA:
        key = f"B_3.8.1_vs_3.3.7_n_{int(s*1000)}mm"
        L.append(f"| {s*100:g} cm | {sum(r[key] for r in righe_task)} | {sum(r[key] >= 1 for r in righe_task)} | {sum(r[key] >= STATI_COLPITO for r in righe_task)} |")
    L.append("\n## Misure secondarie (3.8.1 contro 3.3.7)\n")
    L.append(f"Stati con orientazione diversa ≥ {SOGLIA_ANGOLO:g}°: {sum(r['B_3.8.1_vs_3.3.7_orient_n'] for r in righe_task)}. "
             f"Stati con un cassetto/anta/manopola diverso (≥ {SOGLIA_SCORR*100:g} cm o ≥ {SOGLIA_CERN:g}°): {sum(r['B_3.8.1_vs_3.3.7_artic_n'] for r in righe_task)}.\n")
    L.append("\n## Controlli\n")
    if riassunto["ancora_spatial5"]:
        L.append("Ancora libero_spatial task 5 (distanza xy ciotola–ramekin dopo l'assestamento, media sui 50 stati; valori di Rick0525 in lerobot#4390):\n")
        for v, x in riassunto["ancora_spatial5"].items():
            att = ANCORA_NOTA.get(v)
            L.append(f"- MuJoCo {v}: {x['media_cm']} cm (min {x['min_cm']}, max {x['max_cm']})" + (f"; atteso ≈ {att} cm ± {ANCORA_TOLLERANZA}" if att else ""))
    vs = riassunto.get("verifica_stati_iniziali")
    if vs:
        L.append(f"\nStati iniziali identici fra le versioni (verificato, il confronto si ferma altrimenti): {vs['task_verificati']} task con la stessa impronta SHA-256 "
                 f"del file .pruned_init in 3.3.7, 3.4.0 e 3.8.1; {vs['stati_q0_confrontati']} confronti di stato salvato (q0) a bit, tutti identici.")
    if riassunto["controllo_nullo"]:
        c = riassunto["controllo_nullo"]
        L.append(f"\nControllo nullo (3.3.7 ripetuto con semi 1000+i invece di i): {c['stati_identici_a_bit']}/{c['stati_confrontati']} stati identici a bit. "
                 f"Pavimento del rumore sulla posizione: {c['pavimento_posizione_cm']} cm; stati oltre la soglia di 1 cm per solo rumore: {c['stati_posizione_ge_soglia']}.")
        for k, x in c["task_con_differenze"].items():
            L.append(f"- {k}: {x['stati_diversi_a_bit']} stati diversi a bit, scarto massimo di posizione {x['max_pos_cm']} cm "
                     f"({x['stati_pos_ge_1cm']} stati ≥ 1 cm), massimo scarto su una componente {x['max_scarto_componente']:.3g}")
    else:
        L.append("\nControllo nullo: non eseguito.")
    if riassunto.get("controllo_stesso_seme"):
        L.append("\nRipetizione con lo stesso seme (3.3.7, solo i task che nel controllo nullo differivano): "
                 + "; ".join(f"{k}: {x['identici_a_bit']}/{x['stati']} identici a bit" for k, x in riassunto["controllo_stesso_seme"].items()) + ".")
    pv = riassunto.get("previsioni", {})
    if pv:
        L.append("\n## Previsioni della premessa, verificate\n")
        if "P1" in pv:
            L.append(f"- P1 (spatial/5 colpito in ≥45 stati con 3.4.0 e 3.8.1): {pv['P1']['n_3.4.0']} e {pv['P1']['n_3.8.1']} su 50 → {'vera' if pv['P1']['vera'] else 'FALSA'}.")
        if "P2" in pv:
            L.append(f"- P2 (3.4.0 e 3.8.1 uguali entro 1 mm in ≥90% degli stati, quasi ovunque): {pv['P2']['task_con_90pc_stati_sotto_1mm']} task su {pv['P2']['su']}; "
                     f"scarto massimo di posizione fra 3.4.0 e 3.8.1, a precisione piena: {pv['P2']['max_pos_m_precisione_piena']:.3e} m "
                     f"({pv['P2']['max_pos_m_precisione_piena']*100:.3e} cm); massimo scarto su una qualunque componente (posizione, quaternione, giunti): "
                     f"{pv['P2']['max_componente_precisione_piena']:.3e}; stati identici a bit: {pv['P2']['stati_identici_a_bit']}/{pv['P2']['stati_totali']}, "
                     f"task con tutti i 50 stati identici a bit: {pv['P2']['task_tutti_identici_a_bit']}/{pv['P2']['su']}.")
        if "P3" in pv:
            L.append(f"- P3 (≥30 task su 40 né colpiti né sfiorati): {pv['P3']['task_ok']} su {pv['P3']['su']} → {'vera' if pv['P3']['vera'] else 'FALSA'}.")
        if "P4" in pv:
            L.append(f"- P4 (altri task colpiti più in spatial e libero_10 che in object): task non ok oltre spatial/5 = {pv['P4']['altri_task_non_ok']}; in libero_object: {pv['P4']['in_libero_object']}.")
        if "P5" in pv:
            L.append(f"- P5 (nessun task di libero_goal COLPITO con 3.8.1): colpiti {pv['P5']['libero_goal_task_colpiti']}, stati oltre soglia {pv['P5']['libero_goal_stati_oltre_soglia']}, "
                     f"scarto massimo {pv['P5']['libero_goal_max_cm']} cm.")
    if riassunto.get("estensione_post_hoc"):
        L.append("\n## Estensione post-hoc: assestamento prolungato (NON prevista nella premessa)\n")
        L.append("Stati su 50 con scarto ≥ 1 cm rispetto a 3.3.7 (e mediana dello scarto in cm) dopo 10, 20, 40 e 100 passi; velocità massima mediana degli oggetti (m/s, 3.8.1) a 10 e a 100 passi.\n")
        L.append("| task | confronto | 10 passi | 20 passi | 40 passi | 100 passi | vmax 3.8.1 @10 / @100 |")
        L.append("|---|---|---|---|---|---|---|")
        for r in riassunto["estensione_post_hoc"]:
            for v in ALTRE:
                k = f"{v}_vs_3.3.7"
                L.append(f"| {r['suite']} t{r['task']} | {v} vs 3.3.7 | " + " | ".join(f"{r[f'{k}_p{q}_n']} (med {r[f'{k}_p{q}_mediana_cm']})" for q in (10, 20, 40, 100))
                         + f" | {r['vmax_3.8.1_p10']:.3g} / {r['vmax_3.8.1_p100']:.3g} |")
    if riassunto["mancanti"]:
        L.append("\n## Dati mancanti\n")
        L.extend(f"- {m}" for m in riassunto["mancanti"])
    (out / "tabella_atlante.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
