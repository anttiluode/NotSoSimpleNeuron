from __future__ import annotations

import argparse
import json
from pathlib import Path

from not_so_simple_neuron.active_experiment import run_v1_suite


def main() -> None:
    parser = argparse.ArgumentParser(description="Run NotSoSimpleNeuron v1 active-branch gates")
    parser.add_argument("--seeds", type=int, default=64)
    parser.add_argument("--out", type=Path, default=Path("results/v1.json"))
    args = parser.parse_args()
    if args.seeds < 1:
        raise SystemExit("--seeds must be >= 1")

    result = run_v1_suite(seeds=args.seeds)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
