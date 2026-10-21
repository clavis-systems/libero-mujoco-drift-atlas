# When MuJoCo changes, which LIBERO tasks start differently? A census of all 40 tasks

*Emanuele Rizzan, independent researcher, October 2026.*

## The question

LIBERO starts every episode from 50 saved start states per task. Those saved states are not at rest. Objects hover
above the table or sink into it, and the simulator settles them during `reset()` (LeRobot runs 10 steps with a do-nothing
action). So the start scene a policy sees is partly made by the physics engine.

If a new MuJoCo handles contacts differently, the same file gives a different start scene.
[lerobot#4390](https://github.com/huggingface/lerobot/issues/4390) showed this for **one** task: `libero_spatial`
task 5. I wanted to know about **all 40**.

## What I did

- **Tasks and states:** 4 suites (spatial, object, goal, 10) × 10 tasks × 50 start states = 2,000 start states.
- **Versions:** MuJoCo 3.3.7, 3.4.0 and 3.8.1, with robosuite 1.4.0 and hf-libero 0.1.4. MuJoCo 3.8.1, robosuite and
  hf-libero are the versions of my earlier study ([slow-robot-brain](https://github.com/clavis-systems/slow-robot-brain)).
  I added MuJoCo 3.12.0 afterwards (see its own section).
- **No policy, no GPU, no rendering.** Only the simulator. I copied the reset of LeRobot 0.6.1: seed, hard reset, load
  the saved state, then 10 steps with the action `[0,0,0,0,0,0,-1]`.
- **What I measure:** for every object, how far it ends up after the 10 steps from where the same object ends up in
  MuJoCo 3.3.7 (the larger of the horizontal distance and the height difference).
- **Rules fixed before measuring** (`preregistration/PREMESSA.md`, in Italian):
  - a start state is "hit" if some object differs by **1 cm or more**;
  - a task is **HIT** if at least 5 of its 50 states are hit, **grazed** if 1 to 4.
- **Reference.** 3.3.7 is the last version before the change reported in #4390. It is a reference, not the truth:
  the states were recorded long ago with other versions. I measure differences between versions, not correctness.

## The result

**5 of 40 tasks are HIT and 2 are grazed. 209 of the 2,000 start states differ by 1 cm or more between 3.3.7 and 3.8.1.
3.4.0 and 3.8.1 give the same states to within 5e-12 m: the change happens at 3.4.0 and nothing changes up to 3.8.1.
MuJoCo 3.12.0, added later, changes one task again (see its section).**

| suite | tasks that change (states out of 50) | states out of 500 |
|---|---|---|
| spatial | **5** (50), **8** (5), 2 (2) | 57 |
| object | none | 0 |
| goal | none (largest difference 0.07 cm) | 0 |
| 10 | **0** (50), **1** (50), **7** (50), 6 (2) | 152 |

Bold = HIT. The full table, one row per task, is in `results/tabella_atlante.md` (Italian headings).

**`libero_goal`, the suite I used in my earlier study, does not drift.** With 3.8.1 against 3.3.7: 0 states out of 500
above 1 cm, largest difference 0.7 mm, no orientation difference of 10° or more, no drawer or knob in a different place.

## Two ways to count

| unit | number | what it is |
|---|---|---|
| start states | 209 of 2,000 | episodes that begin with an object moved by 1 cm or more |
| of which repeated | 200 (4 tasks × 50) | `spatial` 5 and `10` 0, 1, 7: the same event in every state |
| of which isolated | 9 (3 tasks) | `spatial` 2 (2 states), `spatial` 8 (5), `10` 6 (2): each its own contact |
| independent events | **2 mechanisms + 9 isolated cases** | the bowl on the ramekin (`spatial` 5); objects saved inside the table (`10`) |

The 50 states of a task change only where the objects sit on the table (x and y), not their height or tilt. So when
the moved object starts at the same height in all 50, one physical event is repeated 50 times.

- **To evaluate a policy, count states.** The policy sees all 50 episodes. In 4 tasks of 40 it sees every one of them
  with an object moved, plus 9 episodes in 3 other tasks.
- **To say how often the simulator changes the physics, count events.** There are two mechanisms and nine contacts,
  not 209 independent cases. "209 of 2,000" does not mean "10% of cases".

## MuJoCo 3.12.0, added later

After the first results I added MuJoCo 3.12.0 (released 20 August 2026), because the maintainers say its box-box collider
was rewritten ([mujoco#3476](https://github.com/google-deepmind/mujoco/issues/3476)). I wrote the plan and my predictions
before measuring (`preregistration/PREMESSA_AGGIUNTA_3.12.md`). Same code, same 1 cm threshold, same classes.

robosuite 1.4.0 does not run on 3.12.0 as it is. Two small changes make it run (`code/robosuite_mujoco312.patch`): an enum
comparison that is false in 3.12.0, and a function whose arguments changed. I checked one start state of `libero_goal`:
the joints of the robot's arm are identical to 12 decimals in patched 3.12.0 and in 3.8.1 after 0, 5 and 10 steps
(`results/controllo_robot_312_*.txt`). That is a check, not a proof for every state.

| 3.12.0 against | HIT tasks | grazed | states of 2,000 above 1 cm |
|---|---|---|---|
| 3.3.7 | 5 (the same five) | 2 | 210 |
| 3.8.1 | 1 | 3 | 55 |

- **The `10` scenes behave as in 3.8.1.** The ketchup flies the same way (peak 1.14 m at step 7) and the engine reports the
  same overlap with the table (2.92 cm, against 1.46 cm in 3.3.7). The rewrite did not go back to the old numbers.
- **`spatial` 5 changes again.** The bowl–ramekin distance is **6.23 cm** (1.45 in 3.3.7, 3.72 in 3.8.1), 6.3 cm away from
  3.8.1 in all 50 states.
- **Small shifts.** In `spatial` 6, 7 and 9 a bowl ends 3.4 mm away from where it ends in both older versions, in every state.
- **Elsewhere** 3.12.0 is within 1 mm of 3.8.1 in at least 90% of the states of 36 tasks out of 40. `libero_goal` does not change.
- **Null control of 3.12.0:** 1,750 of 2,000 states identical, floor 1.26 cm (3 states of `spatial` 4); the same seed gives identical
  results.
- **Predictions.** All five I wrote before measuring came true.

## Why: what I can show and what I cannot

**Tasks `10` 0, 1, 7 (living-room scenes).** Objects such as the ketchup, orange juice and milk are saved inside the
table top. At the saved state the engine reports a contact depth for the same pose that is **exactly double** from 3.4.0 on:

| object | depth in 3.3.7 | depth in 3.8.1 |
|---|---|---|
| ketchup | 1.46 cm | 2.92 cm |
| orange juice, milk | 1.33 cm | 2.65 cm |
| alphabet soup | 0.77 cm | 1.54 cm |
| butter | 0.27 cm | 0.55 cm |

The ketchup is saved at height 0.48 m. With 3.3.7 it rises to 0.65 m and rests at 0.509 m by step 8. With 3.4.0 and
3.8.1 it is thrown up to **1.14 m** (step 7) and at step 10 it is still in the air at 1.3 m/s; by step 20 it has landed at
the same rest height. So the "54 cm" difference at step 10 is mostly a flight, not a different resting place: after 100
steps the difference is 0.65 cm (median), and 3, 0 and 1 states out of 50 are still above 1 cm in tasks 0, 1 and 7.
The objects that move most are bystanders, not the objects named in the instruction.

**This fits the box-box collision fix in MuJoCo 3.4.0 that #4390 points to. It is a strong hint, not a proof.** I did
not read the engine's code, and I did not test the idea directly (for example by lifting the objects out of the table).
What the numbers show is a pattern: in 3.8.1 the three objects that move by tens of centimetres are the three with the
deepest overlap (2.65 to 2.92 cm); the ones with 1.54 cm or less (alphabet soup, butter, cream cheese) do not move by
1 cm, apart from the cream cheese in 3 states of task 0. In `spatial` 5 the states I checked have no overlap at
all, so the mechanism there is different (a bowl that hangs in the air and lands on the rim of the ramekin).

**`spatial` 8, `spatial` 2, `10` 6:** a few states where a bowl or plate slides differently, 1 to 6 cm.
`spatial` 8 is HIT with exactly 5 states, the minimum, and at a 2 cm threshold it would be "grazed". I would not build
a strong sentence on it.

## Checks

- **Positive control.** `spatial` 5, bowl to ramekin distance after settling: 1.45 cm with 3.3.7 and 3.72 cm with 3.4.0
  and 3.8.1, in all 50 states. These are the numbers in #4390. I wrote down in advance that, if my pipeline missed them,
  I would not read anything else.
- **Null control.** I ran 3.3.7 again with different seeds. 1,750 of 2,000 states are identical bit for bit. The other
  250 are in five `spatial` tasks and differ by about 1e-16, except two states of `spatial` 4 that differ by 1.25 cm
  (probably a chaotic contact, not verified). Running again with the **same** seed gives identical results, so the
  difference comes from the seed. The floor of the noise is 1.25 cm, in 2 states of 2,000. Seed noise cannot explain the
  209 hit states: every hit task is identical between the two seeds.
- **Same start states.** The saved-state file has the same SHA-256 in all four versions for all 40 tasks, and the saved
  state of every one of the 2,000 states is bit-identical across versions. The comparison script stops otherwise.
- **No ball joints** in the 40 models (200 free, 63 sliding, 23 hinge joints), so the script misses nothing.
- **Settling is the rule.** In 39 of 40 tasks every state has an object that moves about 4 to 16 cm between the saved
  state and the settled one.
- **5 steps or 10 steps:** the same 209 states.

## Independent review, and what it changed

Codex read the results independently (read-only, it did not run code): `reviews/codex_review_2026-10-21.md`.
It found no error in the numbers and asked for four things, all done: check that the start states match across versions,
give the 3.4.0 vs 3.8.1 difference at full precision, publish the step-by-step path of the ketchup, and check for ball
joints. I also corrected myself while doing it:

- I had written that the ketchup peaks at 1.08 m. That is its height at step 5; the peak is **1.14 m**.
- I had first described the ketchup alone. Orange juice and milk move by 37 to 38 cm in all 50 states of tasks 0 and 1 too.
- I had first counted 209 start states as 209 results. They are two mechanisms and nine contacts (see above).

A separate AI session then recomputed the main numbers from the raw files in `data/`, with its own code written from
the pre-registration, without reading this repository's comparison code: the hit states and classes for all four
versions, 3.4.0 against 3.8.1, both null controls, the bowl–ramekin distances, the 100-step settling and the ketchup
peak. It found the same numbers. Codex has **not** recomputed them, and its review above covers only the first three
versions, not 3.12.0.

## What I did not do

- **No policy scores.** I do not know how much any of this moves a success rate.
- **One machine** (CPU, Linux under WSL, Python 3.12, numpy 2.2.6). My earlier study ran on Kaggle. MuJoCo is not
  guaranteed to be identical across CPUs; the 1 cm threshold is far above numerical noise except in chaotic contacts.
- **Only four MuJoCo versions:** 3.3.7, 3.4.0, 3.8.1 and 3.12.0 (this one with a small compatibility patch to robosuite).
  MuJoCo 3.9 to 3.11 and 3.13 onwards are not measured, and neither is 3.3.2 (the version in the paper below).
  hf-libero 0.1.4 allows `mujoco<3.9`, so 3.12.0 is outside the official pin.
- **Rendering is off.** I assume the physics is the same with cameras on. I did not check this directly; the positive
  control is the indirect check.
- **LIBERO-90 is not included.**
- **The reference is 3.3.7**, not the original recording.

## Related work I found

- [lerobot#4390](https://github.com/huggingface/lerobot/issues/4390) and its pin PR
  [#4465](https://github.com/huggingface/lerobot/pull/4465): one task (`spatial` 5).
- [LIBERO#141](https://github.com/Lifelong-Robot-Learning/LIBERO/issues/141): the same task.
- [simblame](https://github.com/isospin01/simblame) (Apache-2.0): finds the version that breaks `spatial` 5. I did not
  use its code.
- arXiv [2609.37771](https://arxiv.org/abs/2609.37771) audits seven benchmarks. In its appendix (bug 19, which I read
  in the HTML version) it reports that pinning MuJoCo to 3.3.2 instead of 3.8.1 raises the success of π0.5 on
  "pick up bowl" from 62% to 88%, and puts this down to different rendered inputs. It does not name the suite or the
  task number, so I cannot tell whether it is one of the tasks that change in my census. My census has rendering off
  and looks at start states, so it measures a different channel. MuJoCo 3.3.2 is not among my versions.

I found no census of all tasks, and nobody reporting objects saved inside the table (search on 21 October 2026: open
and closed issues and pull requests since 9 August in lerobot, LIBERO, MuJoCo and simblame, plus the paper above). Search
is never complete.

## How this was made

- I directed this work and checked the results. AI coding agents (Claude Code) wrote the code, ran the measurements and
  drafted this text; another AI system (Codex) reviewed the results. I decide what is published and I answer for it.
- The mistakes found along the way are listed above.

## Files

The internal records are in Italian, because that is how I work. The code is commented in Italian.

| Folder | What is inside |
|---|---|
| `preregistration/` | `PREMESSA.md`: the rules, thresholds, predictions and controls, written before the measurements; `PREMESSA_AGGIUNTA_3.12.md`: the dated addition for MuJoCo 3.12.0, also written before measuring |
| `code/` | measurement (`atlante_deriva.py`), comparison (`confronta_atlante.py`, and `confronta_aggiunta.py` for 3.12.0), step-by-step ketchup (`traiettoria_ketchup.py`), model check (`verifica_modelli.py`), saved-state contacts (`contatti_stato_salvato.py`), states against events (`eventi_indipendenti.py`), longer settling (`estensione_assestamento.py`), robot check and patch for 3.12.0 (`controllo_robot_312.py`, `robosuite_mujoco312.patch`), environment and run scripts |
| `data/` | raw measurements per version (`m3.3.7`, `m3.4.0`, `m3.8.1`, `m3.12.0`), null controls, same-seed controls, longer settling, the ketchup paths, package versions in `environment/` |
| `results/` | the tables, per-state CSV, JSON summary, event counts, contacts, ketchup path, and the 3.12.0 files (`aggiunta_3.12.*`) |
| `reviews/` | Codex's review (Italian) |

**To redo the tables** (Python 3 with numpy; no MuJoCo needed, the raw measurements are in `data/`):

```
mkdir results_check
python code/confronta_atlante.py --dati data --out results_check --premessa preregistration/PREMESSA.md
python code/eventi_indipendenti.py --dati data --out results_check
python code/traiettoria_ketchup.py tabella --dati data/traiettoria_ketchup --out results_check/traiettoria_ketchup.txt
python code/confronta_aggiunta.py --dati data --out results_check --contatti results/contatti_stato_salvato.txt results/contatti_stato_salvato_3.12.0.txt
```

These give files identical to `results/` (the first three compare the three first versions; the last one is for 3.12.0). The summary JSON contains the SHA-256 of `PREMESSA.md` and of
`confronta_atlante.py`.

**To redo the measurements** you need MuJoCo, robosuite and hf-libero in separate environments, one per MuJoCo version
(`code/prepara_ambiente.sh`, about 450 MB; the LIBERO assets come from Hugging Face `lerobot/libero-assets`) and about
25 minutes of CPU per version (`code/lancia_misura.sh`). The scripts assume the folder `~/deriva`.

## License

Apache-2.0. The raw files in `data/` contain the object part of LIBERO's saved start states from `hf-libero==0.1.4`
(MIT, © 2023 Lifelong Robot Learning); see `THIRD_PARTY.md`. No LIBERO assets or demonstrations are included.
