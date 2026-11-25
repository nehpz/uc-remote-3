# SPDX-License-Identifier: MPL-2.0

"""Offline checks for the project's supported UC driver archive layout."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tarfile
from pathlib import Path

MAX_ARCHIVE_SIZE = 100_000_000
MAX_METADATA_SIZE = 1_000_000
DRIVER_ID = re.compile(r"[a-z][a-z0-9_-]{4,}\Z")
VERSION = re.compile(
    r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][A-Za-z0-9-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][A-Za-z0-9-]*))*)?"
    r"(?:\+[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*)?\Z"
)


def _archive_path(name: str) -> str:
    # tar commonly emits a single leading "./", including the root directory.
    if name in {".", "./"}:
        return "."
    if name.startswith("./"):
        name = name[2:]
    if "\\" in name or any(part in ("", ".", "..") for part in name.split("/")):
        raise ValueError(f"archive path is not portable: {name!r}")
    return name


def validate_archive(path: Path) -> tuple[str, str]:
    if not path.name.endswith((".tgz", ".tar.gz")):
        raise ValueError("expected a .tgz or .tar.gz archive")
    if path.stat().st_size > MAX_ARCHIVE_SIZE:
        raise ValueError("compressed archive exceeds 100 MB")
    metadata = None
    entrypoints = set()
    members: dict[str, bool] = {}
    total = 0
    with tarfile.open(path, mode="r|gz") as archive:
        for member in archive:
            name = _archive_path(member.name)
            if name == "." and member.isdir():
                continue
            if name in members:
                raise ValueError(f"duplicate path: {name}")
            if len(members) >= 20_000:
                raise ValueError("archive exceeds the lab's 20,000-entry preflight limit")
            if not (member.isfile() or member.isdir()):
                raise ValueError(f"unsupported archive entry (only files and directories): {name}")
            members[name] = member.isdir()
            total += member.size
            if total > 200_000_000:
                raise ValueError("archive exceeds the lab's 200 MB declared-content preflight limit")
            if not member.isdir() and member.mode & 0o111 and not name.startswith("bin/"):
                raise ValueError(f"executable file outside bin/: {name}")
            if name == "driver.json" and member.isfile():
                if member.size > MAX_METADATA_SIZE:
                    raise ValueError("driver.json exceeds the lab's 1 MB preflight limit")
                fileobj = archive.extractfile(member)
                if fileobj is None:
                    raise ValueError("driver.json could not be read")
                with fileobj:
                    metadata = json.load(fileobj)
            if name in {"bin/driver", "bin/driver.js"} and member.isfile():
                if member.size == 0:
                    raise ValueError(f"entry point is empty: {name}")
                if name == "bin/driver" and not member.mode & 0o111:
                    raise ValueError("bin/driver is not executable")
                entrypoints.add(name)

    if not isinstance(metadata, dict):
        raise ValueError("expected a root driver.json object")
    if len(entrypoints) != 1:
        raise ValueError("expected exactly one entry point: bin/driver or bin/driver.js")
    if not isinstance(metadata.get("driver_id"), str) or not DRIVER_ID.fullmatch(metadata["driver_id"]):
        raise ValueError("invalid driver_id")
    if metadata["driver_id"].startswith("uc_"):
        raise ValueError("driver_id uses the reserved uc_ prefix")
    if not isinstance(metadata.get("version"), str) or not VERSION.fullmatch(metadata["version"]):
        raise ValueError("version must use Semantic Versioning")
    name_localizations = metadata.get("name")
    if not isinstance(name_localizations, dict) or not isinstance(name_localizations.get("en"), str) or not name_localizations["en"].strip():
        raise ValueError("expected a nonempty English name in driver.json")
    icon = metadata.get("icon")
    custom_icon = icon.removeprefix("custom:") if isinstance(icon, str) and icon.startswith("custom:") else None
    if custom_icon is not None and (
        not custom_icon.lower().endswith((".png", ".jpg", ".jpeg"))
        or "/" in custom_icon
        or members.get(custom_icon) is not False
    ):
        raise ValueError("expected a root image file for the declared custom icon")
    for name, is_dir in members.items():
        top = name.split("/", 1)[0]
        if top in {"bin", "config", "data"}:
            if name == top and not is_dir:
                raise ValueError(f"expected a directory: {top}")
            components = name.split("/")
            for end in range(1, len(components)):
                if members.get("/".join(components[:end])) is False:
                    raise ValueError(f"archive path has a non-directory parent: {name}")
            continue
        if name != "driver.json" and name != custom_icon:
            raise ValueError(f"unexpected archive root entry: {name}")
    with path.open("rb") as fileobj:
        digest = hashlib.file_digest(fileobj, "sha256").hexdigest()
    return metadata["driver_id"], digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    try:
        driver_id, digest = validate_archive(args.archive)
    except (OSError, ValueError, EOFError, tarfile.TarError) as exc:
        parser.exit(1, f"Archive preflight failed: {exc}\n")
    print(f"Archive layout checks passed for {driver_id}; runtime and device compatibility not verified.")
    print(f"SHA-256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
