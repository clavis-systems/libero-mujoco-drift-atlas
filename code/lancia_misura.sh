#!/usr/bin/env bash
# Lancia l'atlante per una versione di MuJoCo su tutte e quattro le suite, un processo alla volta.
#
# Uso:  bash lancia_misura.sh 3.8.1                   -> ~/deriva/dati/m3.8.1/
#       bash lancia_misura.sh 3.3.7 1000 controllo_nullo   -> ~/deriva/dati/controllo_nullo/m3.3.7/  (semi diversi)
#       SUITE=libero_goal bash lancia_misura.sh 3.8.1      -> solo una suite
set -euo pipefail
V="$1"
SEME="${2:-0}"
SOTTO="${3:-}"
BASE="$HOME/deriva"
QUI="$(cd "$(dirname "$0")" && pwd)"
OUT="$BASE/dati${SOTTO:+/$SOTTO}/m$V"
mkdir -p "$OUT"
export LIBERO_CONFIG_PATH="$BASE/config/$V"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
SUITES="${SUITE:-libero_spatial libero_object libero_goal libero_10}"
for S in $SUITES; do
  "$BASE/venv-$V/bin/python" -I "$QUI/atlante_deriva.py" --suite "$S" --out "$OUT" --seme "$SEME" 2>&1 | tee -a "$OUT/log.txt"
done
echo "FATTO $V -> $OUT"
