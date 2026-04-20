#!/bin/bash
echo "=== Python venv module check ==="
python3 -c "import venv; print('venv module:', venv.__file__)" 2>&1
python3 -m venv --help 2>&1 | head -3
echo
echo "=== virtualenv (standalone) ==="
which virtualenv 2>&1 || echo "(not found system-wide)"
python3 -c "import virtualenv; print('virtualenv pkg:', virtualenv.__file__)" 2>&1
echo
echo "=== conda ==="
which conda 2>&1 || echo "(not found)"
ls -d /opt/conda /home/dengkw/miniconda* /home/dengkw/anaconda* 2>/dev/null
echo
echo "=== pip --user feasibility ==="
pip3 install --user --dry-run --quiet --no-deps tqdm 2>&1 | head -5
echo
echo "=== existing user-installed packages ==="
ls /home/dengkw/.local/lib/python3.10/site-packages/ 2>/dev/null | head -30
echo
echo "=== try installing virtualenv via pip --user (workaround for missing venv) ==="
pip3 install --user virtualenv 2>&1 | tail -5
which virtualenv 2>&1 || echo "(still not on PATH; try ~/.local/bin/virtualenv)"
ls /home/dengkw/.local/bin/virtualenv 2>/dev/null
