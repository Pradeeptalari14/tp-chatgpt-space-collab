#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo " Validating ChatGPT Space Collaboration Broker"
echo "=================================================="

python3 -m py_compile chatgpt_space_broker.py
python3 -m py_compile yjs_crdt_sync_worker.py

python3 chatgpt_space_broker.py
python3 yjs_crdt_sync_worker.py

echo "Validation successful!"
