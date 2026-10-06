"""Download the Superstore order-line CSV (Tableau sample data, mirrored) and verify its checksum."""
import hashlib
import urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/curran/data/gh-pages/superstoreSales/superstoreSales.csv"
SHA256 = "f8e42683eac2118e2708190694f699504aac1b7bab24bcdf727737d8837d085c"
DEST = Path(__file__).resolve().parents[1] / "data" / "raw" / "superstoreSales.csv"


def main() -> None:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if not DEST.exists():
        urllib.request.urlretrieve(URL, DEST)
    digest = hashlib.sha256(DEST.read_bytes()).hexdigest()
    if digest != SHA256:
        raise SystemExit(f"Checksum mismatch for {DEST}: {digest}")
    print(f"Verified {DEST.name} ({digest[:12]}...)")


if __name__ == "__main__":
    main()
