"""Run with a CSV/folder path, or use --pick file / --pick folder."""
import argparse
from pathlib import Path

from app.batch import process_csv


def pick_path(kind):
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        if kind == "folder":
            return filedialog.askdirectory(title="Pilih folder CSV lead", parent=root)
        return filedialog.askopenfilename(title="Pilih CSV lead", filetypes=[("CSV", "*.csv")], parent=root)
    finally:
        root.destroy()


def main():
    parser = argparse.ArgumentParser(description="LeadPilot batch CSV dengan Laya lokal")
    parser.add_argument("path", nargs="?", help="CSV atau folder berisi CSV (tidak rekursif)")
    parser.add_argument("--pick", choices=["file", "folder"])
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "batch_output")
    parser.add_argument("--limit", type=int, help="Batas baris yang dicoba per file pada run ini")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit minimal 1")
    if args.path and args.pick:
        parser.error("Gunakan path atau --pick, bukan keduanya")
    selected = pick_path(args.pick or "file") if not args.path else args.path
    if not selected:
        print("Pemilihan dibatalkan.")
        return 0
    path = Path(selected)
    files = sorted(path.glob("*.csv")) if path.is_dir() else [path]
    if not files:
        print("Folder tidak berisi file CSV.")
        return 1
    failed = False
    try:
        for source in files:
            try:
                _, counts = process_csv(source, args.output, limit=args.limit,
                                        report=lambda message: print(message, flush=True))
                failed |= bool(counts["error"])
            except (OSError, ValueError, UnicodeError) as exc:
                print(f"GAGAL {source.name}: {exc}", flush=True)
                failed = True
    except KeyboardInterrupt:
        print("\nDihentikan. Hasil selesai tersimpan; jalankan lagi input yang sama untuk lanjut.")
        return 130
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
