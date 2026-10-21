#!/usr/bin/env bash
# Prepara ~/deriva in WSL: tre ambienti uv separati (mujoco 3.3.7, 3.4.0, 3.8.1) con le versioni della Legge 1.
# NON tocca ~/robotica. Si lancia SOLO dopo l'OK dell'utente sull'elenco dei pacchetti (PREMESSA.md, sezione Ambiente).
#
# Uso:  bash prepara_ambiente.sh            (tutte e tre le versioni)
#       bash prepara_ambiente.sh 3.8.1      (una sola)
set -euo pipefail

BASE="$HOME/deriva"
PY312="$HOME/.local/share/uv/python/cpython-3.12.15-linux-x86_64-gnu/bin/python3.12"  # interprete già presente, sola lettura
VERSIONI=("${@:-3.3.7 3.4.0 3.8.1}")
read -r -a VERSIONI <<< "${VERSIONI[*]}"

mkdir -p "$BASE/dati" "$BASE/config"
export UV_CACHE_DIR="$BASE/.uv-cache"   # cache propria: non condivide nulla con ~/robotica

echo "[1] uv proprio (download: uv 0.13.4, ~17 MB)"
if [ ! -x "$BASE/.boot/bin/uv" ]; then
  python3 -m venv "$BASE/.boot"
  "$BASE/.boot/bin/pip" install -q "uv==0.13.4"
fi
UV="$BASE/.boot/bin/uv"
"$PY312" --version

echo "[2] asset di LIBERO: copia locale dalla cache già scaricata (nessuna rete)"
if [ ! -d "$BASE/assets" ]; then
  cp -r "$HOME/.cache/libero/assets" "$BASE/assets"
fi
echo "    file copiati: $(find "$BASE/assets" -type f | wc -l)  (originali: $(find "$HOME/.cache/libero/assets" -type f | wc -l))"

# Versioni come nel pip freeze della Legge 1 (fase B); senza torch, lerobot, transformers, wandb.
COMUNI=(
  "numpy==2.2.6" "scipy==1.18.1" "numba==0.68.0" "llvmlite==0.50.0"
  "pillow==12.3.0" "opencv-python-headless==4.13.0.92"
  "matplotlib==3.11.2" "contourpy==1.4.0" "cycler==0.12.1" "fonttools==4.66.1" "kiwisolver==1.5.1"
  "packaging==25.0" "pyparsing==3.3.3" "python-dateutil==2.9.0.post0" "six==1.17.0"
  "imageio==2.38.1" "h5py==3.16.0"
  "gymnasium==1.4.0" "cloudpickle==3.1.2" "typing-extensions==4.16.0" "farama-notifications==0.0.6"
  "easydict==1.13" "pyyaml==6.0.3" "termcolor==3.3.0" "tqdm==4.70.1"
  "networkx==3.6.1" "future==1.0.0"
  "absl-py==2.5.1" "etils[epath]==1.14.0" "zipp==4.1.1" "glfw==2.10.2" "pyopengl==3.1.10"
)

for V in "${VERSIONI[@]}"; do
  AMB="$BASE/venv-$V"
  echo "[3] ambiente mujoco $V in $AMB"
  [ -d "$AMB" ] || "$UV" venv -q -p "$PY312" "$AMB"
  PY="$AMB/bin/python"
  "$UV" pip install -q -p "$PY" "mujoco==$V" "${COMUNI[@]}"
  "$UV" pip install -q -p "$PY" --no-deps "robosuite==1.4.0" "hf-libero==0.1.4" "bddl==1.0.1"

  SP="$("$PY" -c 'import sysconfig;print(sysconfig.get_paths()["purelib"])')"
  # hf-libero cerca gli asset in libero/libero/assets, se esiste, e altrimenti li scarica da Hugging Face:
  # il collegamento alla copia locale evita il download (aggiunto dopo la prima prova, 20/10 19:50).
  [ -e "$SP/libero/libero/assets" ] || ln -s "$BASE/assets" "$SP/libero/libero/assets"
  mkdir -p "$BASE/config/$V"
  cat > "$BASE/config/$V/config.yaml" <<EOF
assets: $BASE/assets
bddl_files: $SP/libero/libero/bddl_files
benchmark_root: $SP/libero/libero
datasets: $SP/libero/datasets
init_states: $SP/libero/libero/init_files
EOF
  echo "    versioni:"; "$UV" pip freeze -p "$PY" > "$BASE/pip_freeze_$V.txt"; grep -i -E "^(mujoco|robosuite|hf-libero|bddl|numpy)==" "$BASE/pip_freeze_$V.txt"
  # prova di importazione (nessun rendering, nessuna rete)
  LIBERO_CONFIG_PATH="$BASE/config/$V" "$PY" -I -c "
import mujoco, robosuite, numpy
import libero.libero as L
from libero.libero.envs.env_wrapper import ControlEnv
print('import OK  mujoco', mujoco.__version__, ' robosuite', robosuite.__version__, ' numpy', numpy.__version__)
" || { echo "IMPORT FALLITO per $V: vedere l'errore sopra (probabile dipendenza mancante: chiedere all'utente)"; exit 1; }
done
du -sh "$BASE"
echo FATTO
