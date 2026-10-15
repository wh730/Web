"""清理指定天数前的本地测试产物；CI 中建议按制品保留策略清理。"""
from pathlib import Path
import argparse
import time

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    cutoff = time.time() - args.days * 86400
    for folder in (ROOT / "artifacts", ROOT / "reports"):
        if not folder.exists():
            continue
        for path in folder.rglob("*"):
            if path.is_file() and path.stat().st_mtime < cutoff:
                print(("would delete " if args.dry_run else "delete ") + str(path))
                if not args.dry_run:
                    path.unlink()
if __name__ == "__main__":
    main()
