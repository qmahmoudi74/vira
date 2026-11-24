"""Create complete, desktop and web release archives."""

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from build import ROOT


ASSET_STEM = "Vira-2.2.0"
COMMON = ("OFL.txt", "FONTLOG.txt", "licenses/NOTICE.txt", "licenses/Roboto-Apache-2.0.txt", "docs/INSTALL.md")


def relative_files(path):
    return sorted(file for file in (ROOT / path).rglob("*") if file.is_file())


def write_archive(path, files):
    with ZipFile(path, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for file in sorted(set(files)):
            archive.write(file, file.relative_to(ROOT).as_posix())
    with ZipFile(path) as archive:
        assert archive.testzip() is None, path


def package(output):
    output.mkdir(parents=True, exist_ok=True)
    common = [ROOT / path for path in COMMON]
    desktop = relative_files("fonts/variable") + relative_files("fonts/static")
    web = relative_files("fonts/web")
    complete = (common + desktop + web + relative_files("docs/assets") + relative_files("specimen")
                + [ROOT / path for path in ("README.md", "Preview.html", "source/Vira.ttx", "requirements.txt",
                                             "scripts/build.py", "scripts/verify.py", "scripts/package.py")])
    assert len(desktop) == 20 and len(web) == 22
    assert all(file.stat().st_size for file in complete)
    archives = {
        f"{ASSET_STEM}.zip": complete,
        f"{ASSET_STEM}-Desktop.zip": common + desktop,
        f"{ASSET_STEM}-Web.zip": common + web,
    }
    for name, files in archives.items():
        write_archive(output / name, files)
    hashes = [f"{sha256((output / name).read_bytes()).hexdigest()}  {name}" for name in archives]
    (output / "SHA256SUMS.txt").write_text("\n".join(hashes) + "\n", encoding="ascii", newline="\n")
    print(*(output / name for name in archives), sep="\n")


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    package(parser.parse_args().output)
