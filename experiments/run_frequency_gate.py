from __future__ import annotations

import argparse
import json
from pathlib import Path

from not_so_simple_neuron.frequency_experiment import run_frequency_gate


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the NotSoSimpleNeuron frequency-addressing gate")
    parser.add_argument("--out", type=Path, default=Path("results/frequency_gate.json"))
    args = parser.parse_args()

    receipt = run_frequency_gate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
