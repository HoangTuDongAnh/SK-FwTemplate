#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTDA Framework Package Setup Wizard

Run from the package root:
  python Tools/setup_wizard.py

This script will:
- Update package.json (name/displayName/description/unity/urls/version optional)
- Rename asmdef names + rootNamespace
- Replace namespace in .cs/.asmdef/.md/.json
- Optionally remove Runtime or Editor parts depending on package type
"""

from __future__ import annotations

import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


TEMPLATE_PACKAGE_ID = "com.htda.framework.template"
TEMPLATE_DISPLAY = "HTDA Framework – Template"
TEMPLATE_NS_ROOT = "HTDA.Framework.Template"
TEMPLATE_ASM_RUNTIME = "HTDA.Framework.Template"
TEMPLATE_ASM_EDITOR = "HTDA.Framework.Template.Editor"
TEMPLATE_REPO_DEFAULT = "HTDA-Framework-Template"

ALLOWED_SUFFIX_RE = re.compile(r"^[a-z0-9]+(\.[a-z0-9]+)*$")


def to_pascal_from_suffix(suffix: str) -> str:
    # editor.tools -> EditorTools, patterns.pooling -> PatternsPooling
    parts = suffix.split(".")
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def iter_text_files(root: Path) -> Iterable[Path]:
    exts = {".cs", ".asmdef", ".md", ".json"}
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() in exts:
            yield p


def safe_read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def safe_write_text(p: Path, content: str) -> None:
    p.write_text(content, encoding="utf-8")


def replace_in_file(p: Path, replacements: list[tuple[str, str]]) -> bool:
    old = safe_read_text(p)
    new = old
    for a, b in replacements:
        new = new.replace(a, b)
    if new != old:
        safe_write_text(p, new)
        return True
    return False


def rename_path_if_exists(src: Path, dst: Path) -> None:
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        src.rename(dst)


def delete_path(p: Path) -> None:
    if not p.exists():
        return
    if p.is_dir():
        shutil.rmtree(p)
    else:
        p.unlink()


@dataclass
class Config:
    suffix: str                 # e.g. core, editor.tools
    module_name: str            # e.g. Core, EditorTools (Pascal)
    display_name: str           # e.g. Core, Editor Tools
    description: str
    unity: str                  # e.g. 2022.3
    version: str                # e.g. 0.1.0
    package_type: str           # runtime-only | editor-only | runtime+editor
    repo_owner: str             # e.g. YourOrg
    repo_prefix: str            # e.g. HTDA-Framework-


def prompt(msg: str, default: str | None = None) -> str:
    if default:
        v = input(f"{msg} [{default}]: ").strip()
        return v if v else default
    return input(f"{msg}: ").strip()


def main() -> None:
    pkg_root = Path(__file__).resolve().parents[1]  # Tools/.. -> package root
    package_json_path = pkg_root / "package.json"
    if not package_json_path.exists():
        raise SystemExit("ERROR: package.json not found. Run wizard from the package root.")

    suffix = prompt("Package suffix (e.g. core, editor.tools, patterns.pooling)", "core")
    suffix = suffix.strip().lower()
    if not ALLOWED_SUFFIX_RE.match(suffix):
        raise SystemExit("ERROR: suffix must match ^[a-z0-9]+(\\.[a-z0-9]+)*$ (example: editor.tools)")

    module_name = prompt("ModuleName (PascalCase, used in namespace/assemblies)", to_pascal_from_suffix(suffix))
    module_name = module_name.strip()
    if not module_name or not re.match(r"^[A-Za-z][A-Za-z0-9]*$", module_name):
        raise SystemExit("ERROR: ModuleName must be PascalCase alphanumeric (e.g. EditorTools)")

    display_name = prompt("Display name", module_name)
    description = prompt("Description", f"HTDA Framework module: {display_name}")

    package_type = prompt("Package type (runtime-only / editor-only / runtime+editor)", "runtime+editor").strip()
    if package_type not in ("runtime-only", "editor-only", "runtime+editor"):
        raise SystemExit("ERROR: package type must be runtime-only, editor-only, or runtime+editor")

    unity = prompt("Minimum Unity version", "2022.3")
    version = prompt("Package version", "0.1.0")

    repo_owner = prompt("GitHub org/user (repo owner)", "<YOUR_ORG>")
    repo_prefix = prompt("Repo prefix", "HTDA-Framework-")
    repo_name = f"{repo_prefix}{module_name}"

    cfg = Config(
        suffix=suffix,
        module_name=module_name,
        display_name=display_name,
        description=description,
        unity=unity,
        version=version,
        package_type=package_type,
        repo_owner=repo_owner,
        repo_prefix=repo_prefix,
    )

    new_package_id = f"com.htda.framework.{cfg.suffix}"
    new_ns_root = f"HTDA.Framework.{cfg.module_name}"
    new_asm_runtime = new_ns_root
    new_asm_editor = f"{new_ns_root}.Editor"

    # 1) Update package.json
    pkg = json.loads(safe_read_text(package_json_path))
    pkg["name"] = new_package_id
    pkg["version"] = cfg.version
    pkg["displayName"] = f"HTDA Framework – {cfg.display_name}"
    pkg["description"] = cfg.description
    pkg["unity"] = cfg.unity

    # Update URLs (best-effort)
    base_repo = f"https://github.com/{cfg.repo_owner}/{repo_name}"
    pkg["documentationUrl"] = base_repo
    pkg["changelogUrl"] = f"{base_repo}/blob/main/CHANGELOG.md"
    pkg["licensesUrl"] = f"{base_repo}/blob/main/LICENSE.md"

    safe_write_text(package_json_path, json.dumps(pkg, indent=2, ensure_ascii=False) + "\n")

    # 2) Remove parts depending on package type
    runtime_dir = pkg_root / "Runtime"
    editor_dir = pkg_root / "Editor"

    if cfg.package_type == "editor-only":
        delete_path(runtime_dir)
    elif cfg.package_type == "runtime-only":
        delete_path(editor_dir)

    # 3) Rename asmdef files if present
    # Runtime asmdef
    rename_path_if_exists(
        pkg_root / "Runtime" / "HTDA.Framework.Template.asmdef",
        pkg_root / "Runtime" / f"{new_asm_runtime}.asmdef"
    )
    # Editor asmdef
    rename_path_if_exists(
        pkg_root / "Editor" / "HTDA.Framework.Template.Editor.asmdef",
        pkg_root / "Editor" / f"{new_asm_editor}.asmdef"
    )

    # 4) Replace content tokens in all text files
    replacements = [
        (TEMPLATE_PACKAGE_ID, new_package_id),
        (TEMPLATE_DISPLAY, f"HTDA Framework – {cfg.display_name}"),
        (TEMPLATE_NS_ROOT, new_ns_root),
        (TEMPLATE_ASM_RUNTIME, new_asm_runtime),
        (TEMPLATE_ASM_EDITOR, new_asm_editor),
        (TEMPLATE_REPO_DEFAULT, repo_name),
        ("<YOUR_ORG>", cfg.repo_owner),
    ]

    changed = 0
    for f in iter_text_files(pkg_root):
        # skip the wizard itself to avoid accidental replacement (optional)
        if f.name == "setup_wizard.py":
            continue
        if replace_in_file(f, replacements):
            changed += 1

    # 5) Rename folder path Template -> ModuleName (best-effort)
    # Runtime folder rename
    rename_path_if_exists(
        pkg_root / "Runtime" / "HTDA" / "Framework" / "Template",
        pkg_root / "Runtime" / "HTDA" / "Framework" / cfg.module_name
    )
    # Editor folder rename
    rename_path_if_exists(
        pkg_root / "Editor" / "HTDA" / "Framework" / "Template",
        pkg_root / "Editor" / "HTDA" / "Framework" / cfg.module_name
    )

    # If editor folder has Editor subfolder path
    rename_path_if_exists(
        pkg_root / "Editor" / "HTDA" / "Framework" / cfg.module_name / "Editor",
        pkg_root / "Editor" / "HTDA" / "Framework" / cfg.module_name / "Editor"
    )

    # 6) Final message
    print("\n✅ HTDA Framework package initialized!")
    print(f"- Package: {new_package_id}")
    print(f"- Namespace: {new_ns_root}")
    print(f"- Assemblies: {new_asm_runtime}" + (f", {new_asm_editor}" if cfg.package_type != "runtime-only" else ""))
    print(f"- Repo (suggested): {repo_name}")
    print(f"- Updated files: {changed}\n")

    # Optional: self-destruct
    remove = prompt("Delete this setup wizard now? (y/N)", "N").strip().lower()
    if remove == "y":
        delete_path(Path(__file__).resolve())
        print("🧹 Wizard deleted.")


if __name__ == "__main__":
    main()