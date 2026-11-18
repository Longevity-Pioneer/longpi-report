"""A temporary copy of the release registry with only the 1.1.1 core terms (core.*), for tests that compare with 1.1.1."""
import atexit
import shutil
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))

from lp import registry as RG  # noqa: E402

_DIR = None


def path() -> Path:
    global _DIR
    if _DIR is None:
        tmp = Path(tempfile.mkdtemp(prefix="longpi-core-reg-"))
        atexit.register(shutil.rmtree, tmp, True)
        dst = tmp / "registry"
        shutil.copytree(SKILL / "registry", dst)
        for p in (dst / "terms").glob("ext.*.json"):
            p.unlink()
        for p in (dst / "qualitative").glob("*.json"):
            p.unlink()
        RG.freeze(dst)
        _DIR = dst
    return _DIR
