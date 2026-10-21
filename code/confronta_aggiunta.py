#!/usr/bin/env python3
"""Aggiunta del 21/10/2026: confronta MuJoCo 3.12.0 con 3.3.7 (riferimento) e con 3.8.1.

Segue `PREMESSA_AGGIUNTA_3.12.md` (scritta prima di misurare). Stesse soglie e stesse classi di `confronta_atlante.py`, di cui
importa le funzioni senza modificarlo (i suoi hash restano validi). Uso (solo numpy):

    python confronta_aggiunta.py --dati data --out results --contatti results/contatti_stato_salvato_3.12.0.txt

Si ferma se gli stati iniziali non sono identici a quelli di 3.3.7 (impronta del file e stato salvato q0 a bit).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

import numpy as np

QUI = Path(__file__).resolve().parent


def _carica_modulo(nome):
    spec = importlib.util.spec_from_file_location(nome, QUI / f"{nome}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


cf = _carica_modulo("confronta_atlante")
ev = _carica_modulo("eventi_indipendenti")
NUOVA, RIF, ALTRA = "3.12.0", "3.3.7", "3.8.1"
SUITES = cf.SUITES


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dati", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--contatti", nargs="+", default=[], help="file(s) prodotti da contatti_stato_salvato.py (una o più versioni)")
    ap.add_argument("--aggiunta", default=str(QUI.parent / "preregistration" / "PREMESSA_AGGIUNTA_3.12.md"))
    args = ap.parse_args()
    dati, out = Path(args.dati), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    righe_task, righe_stato, eventi = [], [], []
    ancora = {}
    verifica = {"task_verificati": 0, "stati_q0_confrontati": 0}
    mancanti = []
    for suite in SUITES:
        for t in range(10):
            dn, dr, da = (cf.carica(dati, v, suite, t) for v in (NUOVA, RIF, ALTRA))
            if dn is None or dr is None or da is None:
                mancanti.append(f"{suite} t{t}")
                continue
            tipi, nomi = dr["tipi"], dr["nomi"]
            if not (np.array_equal(dn["nomi"], nomi) and np.array_equal(dn["tipi"], tipi)):
                raise SystemExit(f"{suite} t{t}: i giunti degli oggetti differiscono fra {RIF} e {NUOVA}")
            h = {v: ((cf.meta(dati, v, suite) or {}).get("task", {}).get(str(t), {}).get("sha256_init")) for v in (RIF, NUOVA)}
            if None in h.values() or h[RIF] != h[NUOVA]:
                raise SystemExit(f"{suite} t{t}: impronta del file degli stati iniziali mancante o diversa: {h}")
            n = dr["q10"].shape[0]
            diversi = [i for i in range(n) if not np.array_equal(dr["q0"][i], dn["q0"][i])]
            if diversi:
                raise SystemExit(f"{suite} t{t}: stato salvato (q0) diverso fra {RIF} e {NUOVA} negli stati {diversi[:5]}")
            verifica["task_verificati"] += 1
            verifica["stati_q0_confrontati"] += n
            nome = (cf.meta(dati, RIF, suite) or {}).get("task", {}).get(str(t), {}).get("nome", f"task{t}")
            rec = {"suite": suite, "task": t, "nome": nome, "n_stati": n}
            posA, _, _, _ = cf.scarti(dn["q0"], dn["q10"], tipi)
            rec["A_3.12.0_n"] = int((posA >= cf.SOGLIA_POS).sum())
            rec["vmax_3.12.0"] = float(dn["vmax"].max())
            for etichetta, altro in (("vs_3.3.7", dr), ("vs_3.8.1", da)):
                pos, ang, sc, ce = cf.scarti(dn["q10"], altro["q10"], tipi)
                pos5, _, _, _ = cf.scarti(dn["q5"], altro["q5"], tipi)
                rec[f"B_{etichetta}_n"] = int((pos >= cf.SOGLIA_POS).sum())
                rec[f"B_{etichetta}_max_cm"] = round(float(pos.max()) * 100, 4)
                rec[f"B_{etichetta}_max_m_esatto"] = float(pos.max())
                rec[f"B_{etichetta}_n_5passi"] = int((pos5 >= cf.SOGLIA_POS).sum())
                rec[f"B_{etichetta}_orient_n"] = int((ang >= cf.SOGLIA_ANGOLO).sum())
                rec[f"B_{etichetta}_artic_n"] = int(((sc >= cf.SOGLIA_SCORR) | (ce >= cf.SOGLIA_CERN)).sum())
                for s in cf.SENSIBILITA:
                    rec[f"B_{etichetta}_n_{int(s * 1000)}mm"] = int((pos >= s).sum())
                rec[f"B_{etichetta}_classe"] = cf.classe(rec[f"B_{etichetta}_n"])
                rec[f"B_{etichetta}_identici_a_bit"] = int(sum(np.array_equal(dn["q10"][i], altro["q10"][i]) for i in range(n)))
                for i in range(n):
                    righe_stato.append({"suite": suite, "task": t, "stato": i, "coppia": f"3.12.0_{etichetta}",
                                        "scarto_pos_cm": round(float(pos[i]) * 100, 4), "scarto_orient_gradi": round(float(ang[i]), 3)})
            if rec["B_vs_3.8.1_n_1mm"] >= 40:  # scarto piccolo ma presente in (quasi) tutti gli stati: chi si muove?
                chi = cf.per_oggetto(dn["q10"], da["q10"], tipi, nomi)
                rec["oggetto_scarto_sistematico_vs_3.8.1"] = f"{chi[0][0]} ({chi[0][1] * 100:.2f} cm)" if chi else "-"
            if suite == "libero_spatial" and t == 5:
                for v, d in ((RIF, dr), (ALTRA, da), (NUOVA, dn)):
                    dist = cf.distanza_ciotola_ramekin(d["q10"], d["q0"], tipi, nomi) * 100
                    ancora[v] = {"media_cm": round(float(np.nanmean(dist)), 2), "min_cm": round(float(np.nanmin(dist)), 2),
                                 "max_cm": round(float(np.nanmax(dist)), 2)}
            righe_task.append(rec)
            # eventi: oggetti che si spostano >= 1 cm rispetto a 3.3.7
            for k in np.where(tipi == 0)[0]:
                d = dn["q10"][:, k, :3] - dr["q10"][:, k, :3]
                mag = np.maximum(np.linalg.norm(d[:, :2], axis=1), np.abs(d[:, 2]))
                colpiti = np.where(mag >= cf.SOGLIA_POS)[0]
                if len(colpiti) == 0:
                    continue
                q0 = dr["q0"][:, k, :]
                reps_b, _ = ev.cluster(range(n), lambda i, j: abs(q0[i, 2] - q0[j, 2]) <= ev.TOL_POS and ev.angolo_gradi(q0[i, 3:], q0[j, 3:]) <= ev.TOL_ANGOLO)
                reps_c, _ = ev.cluster(list(colpiti), lambda i, j: np.linalg.norm(d[i] - d[j]) <= ev.TOL_POS)
                eventi.append({"suite": suite, "task": t, "oggetto": str(nomi[k]).split("|")[0], "stati_colpiti": int(len(colpiti)),
                               "pose_quota_orientazione_distinte_su_50": len(reps_b), "esiti_distinti": len(reps_c),
                               "scarto_max_cm": round(float(mag.max()) * 100, 2)})

    # controllo nullo di 3.12.0 (semi 1000+i)
    nullo = None
    base_nullo = dati / "controllo_nullo_312"
    if (base_nullo / f"m{NUOVA}").exists():
        conf, ugu, max_pos, n_ge, per_task = 0, 0, 0.0, 0, {}
        for suite in SUITES:
            for t in range(10):
                a, b = cf.carica(dati, NUOVA, suite, t), cf.carica(base_nullo, NUOVA, suite, t)
                if a is None or b is None:
                    continue
                if not np.array_equal(a["q0"], b["q0"]):
                    raise SystemExit(f"{suite} t{t}: controllo nullo 3.12.0 con stati salvati diversi")
                n = a["q10"].shape[0]
                u = int(sum(np.array_equal(a["q10"][i], b["q10"][i]) for i in range(n)))
                pos, _, _, _ = cf.scarti(a["q10"], b["q10"], a["tipi"])
                conf += n
                ugu += u
                max_pos = max(max_pos, float(pos.max()))
                n_ge += int((pos >= cf.SOGLIA_POS).sum())
                if u < n:
                    per_task[f"{suite} t{t}"] = {"stati_diversi_a_bit": n - u, "max_pos_cm": round(float(pos.max()) * 100, 4),
                                                 "stati_pos_ge_1cm": int((pos >= cf.SOGLIA_POS).sum())}
        nullo = None if conf == 0 else {"stati_confrontati": conf, "stati_identici_a_bit": ugu, "pavimento_posizione_cm": round(max_pos * 100, 4),
                 "stati_posizione_ge_soglia": n_ge, "task_con_differenze": per_task}

    # ripetizione a stesso seme (solo i task che nel controllo nullo differivano)
    stesso = None
    base_stesso = dati / "controllo_stesso_seme_312"
    if (base_stesso / f"m{NUOVA}").exists():
        stesso = {}
        for suite in SUITES:
            for t in range(10):
                a, b = cf.carica(dati, NUOVA, suite, t), cf.carica(base_stesso, NUOVA, suite, t)
                if a is None or b is None:
                    continue
                n = a["q10"].shape[0]
                stesso[f"{suite} t{t}"] = {"stati": n, "identici_a_bit": int(sum(np.array_equal(a["q10"][i], b["q10"][i]) for i in range(n)))}

    # traiettoria del ketchup
    ketchup = {}
    for v in (RIF, ALTRA, NUOVA):
        for t in (0, 1, 7):
            f = dati / "traiettoria_ketchup" / f"m{v}_t{t}.json"
            if not f.exists():
                continue
            r = json.loads(f.read_text(encoding="utf-8"))
            z, vel = r["z"], r["velocita"]
            picchi = sorted(max(zz) for zz in z)
            ketchup[f"{v}_t{t}"] = {"picco_mediano_m": round(picchi[len(picchi) // 2], 4),
                                    "passo_picco_stato0": int(z[0].index(max(z[0]))),
                                    "z_passo10_stato0": round(z[0][10], 4), "v_passo10_stato0": round(vel[0][10], 4),
                                    "z_passo20_stato0": round(z[0][20], 4), "z_passo100_stato0": round(z[0][100], 4)}

    # profondità di compenetrazione del ketchup allo stato salvato (da contatti_stato_salvato.py, task 0 stato 0)
    profondita = {}
    testi = [Path(c).read_text(encoding="utf-8") for c in args.contatti if Path(c).exists()]
    if testi:
        testo = "\n".join(testi)
        blocchi = re.split(r"(?=^MuJoCo [0-9.]+ )", testo, flags=re.M)
        for b in blocchi:
            m = re.match(r"MuJoCo ([0-9.]+)", b)
            if not m:
                continue
            k = re.search(r"libero_10 task 0 stato 0.*?ketchup_1_main: peggiore (-?[0-9.]+) cm", b, flags=re.S)
            if k:
                profondita[m.group(1)] = float(k.group(1))

    # previsioni Q1-Q5
    pv = {}
    if righe_task:
        n_1mm = [r["B_vs_3.8.1_n_1mm"] for r in righe_task]
        q1 = sum(1 for x in n_1mm if x <= 5)
        pv["Q1"] = {"task_con_90pc_stati_entro_1mm_da_3.8.1": q1, "su": len(righe_task), "soglia": 35, "vera": q1 >= 35}
        per = {(r["suite"], r["task"]): r for r in righe_task}
        att = [("libero_spatial", 5), ("libero_10", 0), ("libero_10", 1), ("libero_10", 7)]
        stato = {f"{s} t{t}": per[(s, t)]["B_vs_3.3.7_classe"] for s, t in att if (s, t) in per}
        pv["Q2"] = {"classi_contro_3.3.7": stato, "vera": all(c == "COLPITO" for c in stato.values()) and len(stato) == 4}
        goal = [r for r in righe_task if r["suite"] == "libero_goal"]
        pv["Q3"] = {"libero_goal_task_colpiti": sum(r["B_vs_3.3.7_classe"] == "COLPITO" for r in goal),
                    "stati_oltre_soglia": sum(r["B_vs_3.3.7_n"] for r in goal), "vera": sum(r["B_vs_3.3.7_classe"] == "COLPITO" for r in goal) == 0}
        picchi = [v["picco_mediano_m"] for k, v in ketchup.items() if k.startswith(NUOVA)]
        pv["Q4"] = {"picchi_ketchup_3.12.0_m": picchi, "vera": (min(picchi) > 0.8) if picchi else None}
        if NUOVA in profondita:
            pv["Q5"] = {"profondita_ketchup_3.12.0_cm": profondita[NUOVA], "profondita_3.8.1_cm": profondita.get("3.8.1"),
                        "profondita_3.3.7_cm": profondita.get("3.3.7"), "entro_5pc_di_3.8.1": abs(abs(profondita[NUOVA]) - 2.92) <= 0.05 * 2.92}

    riassunto = {"sha256_aggiunta": hashlib.sha256(Path(args.aggiunta).read_bytes()).hexdigest() if Path(args.aggiunta).exists() else None,
                 "sha256_confronta_aggiunta": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 "verifica_stati_iniziali": verifica, "mancanti": mancanti, "task": {f"{r['suite']} t{r['task']}": r for r in righe_task},
                 "eventi": eventi, "controllo_nullo_3.12.0": nullo, "controllo_stesso_seme_3.12.0": stesso, "ketchup": ketchup, "profondita_ketchup_cm": profondita, "ancora_spatial5": ancora, "previsioni": pv}
    (out / "aggiunta_3.12.json").write_text(json.dumps(riassunto, indent=1, ensure_ascii=False), encoding="utf-8")
    with open(out / "aggiunta_3.12_per_stato.csv", "w", newline="", encoding="utf-8") as f:
        if righe_stato:
            w = csv.DictWriter(f, fieldnames=list(righe_stato[0].keys()))
            w.writeheader()
            w.writerows(righe_stato)

    L = ["# Aggiunta: MuJoCo 3.12.0 (soglie e classi invariate; riferimento 3.3.7; confronto anche con 3.8.1)\n"]
    L.append(f"Stati iniziali identici a 3.3.7 (verificato, altrimenti il confronto si ferma): {verifica['task_verificati']} task con la stessa impronta del file, "
             f"{verifica['stati_q0_confrontati']} stati salvati identici a bit.\n")
    for suite in SUITES:
        rs = [r for r in righe_task if r["suite"] == suite]
        if not rs:
            continue
        L.append(f"\n## {suite}\n")
        L.append("| task | A 3.12.0 | vs 3.3.7: stati ≥1 cm | max cm | classe | vs 3.8.1: stati ≥1 cm | max cm | stati ≥1 mm | identici a bit |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for r in rs:
            L.append(f"| {r['task']} | {r['A_3.12.0_n']} | {r['B_vs_3.3.7_n']} | {r['B_vs_3.3.7_max_cm']} | {r['B_vs_3.3.7_classe']} | "
                     f"{r['B_vs_3.8.1_n']} | {r['B_vs_3.8.1_max_cm']} | {r['B_vs_3.8.1_n_1mm']} | {r['B_vs_3.8.1_identici_a_bit']}/50 |")
        col = sum(r["B_vs_3.3.7_classe"] == "COLPITO" for r in rs)
        sf = sum(r["B_vs_3.3.7_classe"] == "sfiorato" for r in rs)
        L.append(f"\nSintesi {suite}: contro 3.3.7 {col} COLPITI, {sf} sfiorati, {sum(r['B_vs_3.3.7_n'] for r in rs)} stati su {sum(r['n_stati'] for r in rs)}; "
                 f"contro 3.8.1 {sum(r['B_vs_3.8.1_n'] for r in rs)} stati oltre 1 cm.")
    if righe_task:
        L.append("\n## Totali\n")
        for et in ("vs_3.3.7", "vs_3.8.1"):
            col = sum(r[f"B_{et}_classe"] == "COLPITO" for r in righe_task)
            sf = sum(r[f"B_{et}_classe"] == "sfiorato" for r in righe_task)
            L.append(f"- 3.12.0 {et}: {col} task COLPITI, {sf} sfiorati, {sum(r[f'B_{et}_n'] for r in righe_task)} stati su {sum(r['n_stati'] for r in righe_task)} oltre 1 cm; "
                     f"scarto massimo {max(r[f'B_{et}_max_m_esatto'] for r in righe_task):.3e} m.")
        L.append("\nSensibilità (3.12.0 contro 3.3.7): " + "; ".join(
            f"{s*100:g} cm → {sum(r[f'B_vs_3.3.7_n_{int(s*1000)}mm'] for r in righe_task)} stati, "
            f"{sum(r[f'B_vs_3.3.7_n_{int(s*1000)}mm'] >= cf.STATI_COLPITO for r in righe_task)} task COLPITI" for s in cf.SENSIBILITA) + ".")
    if eventi:
        L.append("\n## Oggetti che si spostano ≥ 1 cm rispetto a 3.3.7 (stati contro eventi)\n")
        L.append("| task | oggetto | stati colpiti | pose distinte (quota+orientazione) su 50 | esiti distinti | scarto max cm |")
        L.append("|---|---|---|---|---|---|")
        for e in eventi:
            L.append(f"| {e['suite'].replace('libero_', '')} t{e['task']} | {e['oggetto']} | {e['stati_colpiti']} | {e['pose_quota_orientazione_distinte_su_50']} | {e['esiti_distinti']} | {e['scarto_max_cm']} |")
    if not nullo:
        L.append("\n## Controllo nullo di 3.12.0\n\nNon ancora eseguito.")
    if nullo:
        L.append(f"\n## Controllo nullo di 3.12.0 (semi 1000+i)\n\n{nullo['stati_identici_a_bit']}/{nullo['stati_confrontati']} stati identici a bit; pavimento del rumore sulla "
                 f"posizione {nullo['pavimento_posizione_cm']} cm; stati oltre 1 cm per solo rumore: {nullo['stati_posizione_ge_soglia']}.")
        for k, x in nullo["task_con_differenze"].items():
            L.append(f"- {k}: {x['stati_diversi_a_bit']} stati diversi, massimo {x['max_pos_cm']} cm ({x['stati_pos_ge_1cm']} stati ≥ 1 cm)")
        if stesso:
            L.append("Ripetizione con lo stesso seme (3.12.0, solo i task che differivano): "
                     + "; ".join(f"{k}: {x['identici_a_bit']}/{x['stati']} identici a bit" for k, x in stesso.items()) + ".")
    if ketchup:
        L.append("\n## Ketchup di libero_10 (stato 0; il percorso è identico in tutti i 50 stati)\n")
        L.append("| versione | task | picco mediano (m) | passo del picco | z al passo 10 (m) | velocità al passo 10 (m/s) | z al passo 20 | z al passo 100 |")
        L.append("|---|---|---|---|---|---|---|---|")
        for k, x in sorted(ketchup.items()):
            v, tt = k.split("_t")
            L.append(f"| {v} | {tt} | {x['picco_mediano_m']} | {x['passo_picco_stato0']} | {x['z_passo10_stato0']} | {x['v_passo10_stato0']} | {x['z_passo20_stato0']} | {x['z_passo100_stato0']} |")
    if profondita:
        L.append("\nCompenetrazione del ketchup nel tavolo allo stato salvato (libero_10 task 0 stato 0): "
                 + ", ".join(f"{v}: {abs(p)} cm" for v, p in sorted(profondita.items())) + ".")
    if ancora:
        L.append("\nAncora `libero_spatial` task 5 (distanza xy ciotola–ramekin dopo l'assestamento, media sui 50 stati; i valori di lerobot#4390 valgono fino a 3.8.1; per 3.12.0 è un dato, non un cancello): "
                 + "; ".join(f"{v}: {x['media_cm']} cm (min {x['min_cm']}, max {x['max_cm']})" for v, x in ancora.items()) + ".")
    sistematici = [(r["suite"], r["task"], r["oggetto_scarto_sistematico_vs_3.8.1"], r["B_vs_3.8.1_n_1mm"]) for r in righe_task if "oggetto_scarto_sistematico_vs_3.8.1" in r]
    if sistematici:
        L.append("\nTask in cui 3.12.0 differisce da 3.8.1 di almeno 1 mm in (quasi) tutti i 50 stati, con l'oggetto che si sposta di più (mediana): "
                 + "; ".join(f"{s.replace('libero_', '')} t{t}: {o} in {n} stati" for s, t, o, n in sistematici) + ".")
    if pv:
        L.append("\n## Previsioni dell'aggiunta, verificate\n")
        if "Q1" in pv:
            L.append(f"- Q1 (3.12.0 e 3.8.1 entro 1 mm in ≥90% degli stati di almeno 35 task): {pv['Q1']['task_con_90pc_stati_entro_1mm_da_3.8.1']} task su {pv['Q1']['su']} → {'vera' if pv['Q1']['vera'] else 'FALSA'}.")
        if "Q2" in pv:
            L.append(f"- Q2 (3.12.0 non torna a 3.3.7: spatial/5 e libero_10 0, 1, 7 COLPITI): {pv['Q2']['classi_contro_3.3.7']} → {'vera' if pv['Q2']['vera'] else 'FALSA'}.")
        if "Q3" in pv:
            L.append(f"- Q3 (nessun task di libero_goal COLPITO): colpiti {pv['Q3']['libero_goal_task_colpiti']}, stati oltre soglia {pv['Q3']['stati_oltre_soglia']} → {'vera' if pv['Q3']['vera'] else 'FALSA'}.")
        if "Q4" in pv:
            L.append(f"- Q4 (picco del ketchup sopra 0,8 m): {pv['Q4']['picchi_ketchup_3.12.0_m']} → "
                     + ("non ancora misurato" if pv['Q4']['vera'] is None else ('vera' if pv['Q4']['vera'] else 'FALSA')) + ".")
        if "Q5" not in pv:
            L.append("- Q5 (profondità del ketchup come 3.8.1): non ancora misurato.")
        if "Q5" in pv:
            L.append(f"- Q5 (profondità del ketchup come 3.8.1, 2,92 cm entro il 5%): 3.12.0 {pv['Q5']['profondita_ketchup_3.12.0_cm']} cm (3.8.1 {pv['Q5']['profondita_3.8.1_cm']}, 3.3.7 {pv['Q5']['profondita_3.3.7_cm']}) → {'vera' if pv['Q5']['entro_5pc_di_3.8.1'] else 'FALSA'}.")
    if mancanti:
        L.append("\nDati mancanti: " + ", ".join(mancanti))
    (out / "aggiunta_3.12.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
