"""Seal the already-completed comparator inputs. No allocation is evaluated."""

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json
import runpy


def main():
    p = ArgumentParser(description=__doc__)
    for name in ("comparator", "evidence", "workspace", "out"):
        p.add_argument("--"+name, type=Path, required=True)
    a = p.parse_args()
    checker = runpy.run_path(str(Path(__file__).with_name("check.py")))
    head = checker["git"](a.comparator, "rev-parse", "HEAD").decode().strip()
    if (a.evidence/"exact-head").read_text().strip() != head:
        raise ValueError("The clean checkout and exact completion head differ")
    for name in checker["LOG_NAMES"]:
        if (a.evidence/f"{name}.exit").read_text().strip() != "0":
            raise ValueError(f"Comparator {name} has no completed success receipt")
    paths = checker["file_paths"](a.comparator, a.evidence, a.workspace)
    manifest = {"head":head,"sha256_by_path":{key:sha256(p.read_bytes()).hexdigest() for key,p in paths.items()}}
    # Reuse only the authentication gate, before any evaluation or profile price.
    checker["authenticated"](a.comparator,a.evidence,a.workspace,manifest)
    with a.out.open("x") as f:
        json.dump(manifest,f,sort_keys=True,indent=2)
        f.write("\n")


if __name__=="__main__":
    main()
