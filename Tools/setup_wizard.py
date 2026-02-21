#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTDA Framework Package Setup Wizard

Run from the package root:
  python Tools/setup_wizard.py

Mục tiêu:
- Chuẩn hoá package theo conventions HTDA Framework (UPM name / asmdef / namespace / docs URLs)
- Cho phép tạo package theo 3 kiểu:
  - runtime-only
  - editor-only
  - runtime+editor
- Tự xoá những phần không cần (vd: editor-only thì xoá Runtime + Tests/Runtime)
- Thay thế token "Template" trong toàn bộ file text phù hợp (.cs/.asmdef/.md/.json)
"""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


# =========================
# 1) TEMPLATE CONSTANTS
# =========================
# Các hằng số dưới đây mô tả "tình trạng trước khi setup" (template gốc).
# Wizard sẽ thay thế các token này sang module mới.

TEMPLATE_PACKAGE_ID = "com.htda.framework.template"
TEMPLATE_DISPLAY = "HTDA Framework – Template"

# Namespace/assemblies của template gốc
TEMPLATE_NS_ROOT = "HTDA.Framework.Template"
TEMPLATE_ASM_RUNTIME = "HTDA.Framework.Template"
TEMPLATE_ASM_EDITOR = "HTDA.Framework.Template.Editor"

# Repo name mặc định (chỉ dùng để replace text trong README/urls nếu có)
TEMPLATE_REPO_DEFAULT = "HTDA-Framework-Template"

# Suffix của package phải là dạng: core | editor.tools | patterns.pooling | ...
ALLOWED_SUFFIX_RE = re.compile(r"^[a-z0-9]+(\.[a-z0-9]+)*$")


# =========================
# 2) SMALL HELPERS
# =========================
def to_pascal_from_suffix(suffix: str) -> str:
    """
    Convert suffix dạng dot-case sang PascalCase (không dùng dấu chấm).
    Ví dụ:
      editor.tools      -> EditorTools
      patterns.pooling  -> PatternsPooling
    """
    parts = suffix.split(".")
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def iter_text_files(root: Path) -> Iterable[Path]:
    """
    Duyệt tất cả file text có thể replace token trong package.
    """
    exts = {".cs", ".asmdef", ".md", ".json"}
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            yield p


def safe_read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def safe_write_text(p: Path, content: str) -> None:
    p.write_text(content, encoding="utf-8")


def replace_in_file(p: Path, replacements: list[tuple[str, str]]) -> bool:
    """
    Replace chuỗi theo replacements (list of (old, new)).
    Trả về True nếu có thay đổi.
    """
    old = safe_read_text(p)
    new = old
    for a, b in replacements:
        new = new.replace(a, b)
    if new != old:
        safe_write_text(p, new)
        return True
    return False


def rename_path_if_exists(src: Path, dst: Path) -> None:
    """
    Rename file/folder nếu tồn tại (best-effort).
    """
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        src.rename(dst)


def delete_path(p: Path) -> None:
    """
    Xoá file/folder nếu tồn tại.
    """
    if not p.exists():
        return
    if p.is_dir():
        shutil.rmtree(p)
    else:
        p.unlink()


def prompt(msg: str, default: Optional[str] = None) -> str:
    """
    Input có default.
    """
    if default is not None and default != "":
        v = input(f"{msg} [{default}]: ").strip()
        return v if v else default
    return input(f"{msg}: ").strip()


def normalize_yes_no(v: str) -> bool:
    v = (v or "").strip().lower()
    return v in ("y", "yes", "1", "true")


# =========================
# 3) CONFIG MODEL
# =========================
@dataclass
class Config:
    # Package suffix, ví dụ: core, editor.tools, patterns.pooling
    suffix: str

    # PascalCase dùng cho namespace/assemblies, ví dụ: Core, EditorTools
    module_name: str

    # Hiển thị trên Package Manager, ví dụ: "Core", "Editor Tools"
    display_name: str

    # Mô tả package
    description: str

    # Minimum Unity version
    unity: str

    # Package version
    version: str

    # runtime-only | editor-only | runtime+editor
    package_type: str

    # Repo metadata (best-effort URLs)
    repo_owner: str
    repo_prefix: str


# =========================
# 4) INPUT + CONFIRM FLOW
# =========================
def collect_config_interactive() -> Config:
    """
    Thu thập input từ user.
    """
    suffix = prompt("Package suffix (e.g. core, editor.tools, patterns.pooling)", "core").strip().lower()
    if not ALLOWED_SUFFIX_RE.match(suffix):
        raise SystemExit("ERROR: suffix must match ^[a-z0-9]+(\\.[a-z0-9]+)*$ (example: editor.tools)")

    module_name_default = to_pascal_from_suffix(suffix)
    module_name = prompt("ModuleName (PascalCase, used in namespace/assemblies)", module_name_default).strip()
    if not module_name or not re.match(r"^[A-Za-z][A-Za-z0-9]*$", module_name):
        raise SystemExit("ERROR: ModuleName must be PascalCase alphanumeric (e.g. EditorTools)")

    display_name = prompt("Display name", module_name).strip()
    description = prompt("Description", f"HTDA Framework module: {display_name}").strip()

    package_type = prompt("Package type (runtime-only / editor-only / runtime+editor)", "runtime+editor").strip()
    if package_type not in ("runtime-only", "editor-only", "runtime+editor"):
        raise SystemExit("ERROR: package type must be runtime-only, editor-only, or runtime+editor")

    unity = prompt("Minimum Unity version", "2022.3").strip()
    version = prompt("Package version", "0.1.0").strip()

    repo_owner = prompt("GitHub org/user (repo owner)", "<YOUR_ORG>").strip()
    repo_prefix = prompt("Repo prefix", "HTDA-Framework-").strip()

    return Config(
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


def print_summary(cfg: Config) -> None:
    """
    In summary để user confirm.
    """
    new_package_id = f"com.htda.framework.{cfg.suffix}"
    new_ns_root = f"HTDA.Framework.{cfg.module_name}"
    new_asm_runtime = new_ns_root
    new_asm_editor = f"{new_ns_root}.Editor"
    repo_name = f"{cfg.repo_prefix}{cfg.module_name}"

    print("\n==================== SETUP SUMMARY ====================")
    print(f"Package ID      : {new_package_id}")
    print(f"Display Name    : HTDA Framework – {cfg.display_name}")
    print(f"Description     : {cfg.description}")
    print(f"Unity Min       : {cfg.unity}")
    print(f"Version         : {cfg.version}")
    print(f"Package Type    : {cfg.package_type}")
    print(f"Namespace Root  : {new_ns_root}")
    if cfg.package_type == "runtime-only":
        print(f"Assemblies      : {new_asm_runtime}")
    elif cfg.package_type == "editor-only":
        print(f"Assemblies      : {new_asm_editor} (Editor-only)")
    else:
        print(f"Assemblies      : {new_asm_runtime}, {new_asm_editor}")
    print(f"Repo (suggested): {repo_name}")
    print("=======================================================\n")


def confirm_and_edit(cfg: Config) -> Config:
    """
    Cho user xem lại và sửa nhanh trước khi thực thi.
    Flow:
      - show summary
      - ask confirm
      - nếu muốn chỉnh: chọn field để sửa, rồi show lại summary
    """
    while True:
        print_summary(cfg)
        ans = prompt("Proceed with these settings? (Y to continue / E to edit / N to cancel)", "Y").strip().lower()

        if ans in ("y", "yes"):
            return cfg
        if ans in ("n", "no"):
            raise SystemExit("Cancelled by user.")
        if ans in ("e", "edit"):
            # Menu edit nhanh
            print("Which field do you want to edit?")
            print("1) suffix")
            print("2) module_name")
            print("3) display_name")
            print("4) description")
            print("5) unity")
            print("6) version")
            print("7) package_type")
            print("8) repo_owner")
            print("9) repo_prefix")
            choice = prompt("Select 1-9", "").strip()

            if choice == "1":
                v = prompt("suffix", cfg.suffix).strip().lower()
                if not ALLOWED_SUFFIX_RE.match(v):
                    print("Invalid suffix format. Keeping previous value.")
                else:
                    cfg.suffix = v
            elif choice == "2":
                v = prompt("module_name", cfg.module_name).strip()
                if not re.match(r"^[A-Za-z][A-Za-z0-9]*$", v):
                    print("Invalid ModuleName. Keeping previous value.")
                else:
                    cfg.module_name = v
            elif choice == "3":
                cfg.display_name = prompt("display_name", cfg.display_name).strip()
            elif choice == "4":
                cfg.description = prompt("description", cfg.description).strip()
            elif choice == "5":
                cfg.unity = prompt("unity", cfg.unity).strip()
            elif choice == "6":
                cfg.version = prompt("version", cfg.version).strip()
            elif choice == "7":
                v = prompt("package_type (runtime-only/editor-only/runtime+editor)", cfg.package_type).strip()
                if v not in ("runtime-only", "editor-only", "runtime+editor"):
                    print("Invalid package type. Keeping previous value.")
                else:
                    cfg.package_type = v
            elif choice == "8":
                cfg.repo_owner = prompt("repo_owner", cfg.repo_owner).strip()
            elif choice == "9":
                cfg.repo_prefix = prompt("repo_prefix", cfg.repo_prefix).strip()
            else:
                print("Unknown selection. No changes made.")

            # Nếu suffix thay đổi mà user không đổi module_name,
            # bạn có thể tự sync module_name theo suffix nếu muốn.
            # Ở đây mình không auto để tránh overwrite ý user.
            continue

        # Nếu input khác Y/E/N
        print("Please input Y, E, or N.")


# =========================
# 5) APPLY CHANGES
# =========================
def apply_setup(pkg_root: Path, cfg: Config) -> None:
    """
    Thực thi setup: update package.json, remove parts, rename asmdef, replace tokens, rename folders.
    """
    package_json_path = pkg_root / "package.json"
    if not package_json_path.exists():
        raise SystemExit("ERROR: package.json not found. Run wizard from the package root.")

    # Các giá trị đích
    new_package_id = f"com.htda.framework.{cfg.suffix}"
    new_ns_root = f"HTDA.Framework.{cfg.module_name}"
    new_asm_runtime = new_ns_root
    new_asm_editor = f"{new_ns_root}.Editor"
    repo_name = f"{cfg.repo_prefix}{cfg.module_name}"

    # -------------------------
    # Step 1: Update package.json
    # -------------------------
    pkg = json.loads(safe_read_text(package_json_path))
    pkg["name"] = new_package_id
    pkg["version"] = cfg.version
    pkg["displayName"] = f"HTDA Framework – {cfg.display_name}"
    pkg["description"] = cfg.description
    pkg["unity"] = cfg.unity

    # URLs best-effort (không bắt buộc user phải đặt repo theo y hệt, nhưng giúp docs link đúng)
    base_repo = f"https://github.com/{cfg.repo_owner}/{repo_name}"
    pkg["documentationUrl"] = base_repo
    pkg["changelogUrl"] = f"{base_repo}/blob/main/CHANGELOG.md"
    pkg["licensesUrl"] = f"{base_repo}/blob/main/LICENSE.md"

    safe_write_text(package_json_path, json.dumps(pkg, indent=2, ensure_ascii=False) + "\n")

    # -------------------------
    # Step 2: Remove parts depending on package type
    # - editor-only: remove Runtime + Tests/Runtime
    # - runtime-only: remove Editor + Tests/Editor
    # -------------------------
    runtime_dir = pkg_root / "Runtime"
    editor_dir = pkg_root / "Editor"
    tests_runtime_dir = pkg_root / "Tests" / "Runtime"
    tests_editor_dir = pkg_root / "Tests" / "Editor"

    if cfg.package_type == "editor-only":
        delete_path(runtime_dir)
        delete_path(tests_runtime_dir)
    elif cfg.package_type == "runtime-only":
        delete_path(editor_dir)
        delete_path(tests_editor_dir)

    # -------------------------
    # Step 3: Rename asmdef files if present
    # -------------------------
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

    # editor-only: đảm bảo Editor asmdef không reference runtime asmdef (vì runtime đã xoá)
    if cfg.package_type == "editor-only":
        editor_asmdef = pkg_root / "Editor" / f"{new_asm_editor}.asmdef"
        if editor_asmdef.exists():
            asm = json.loads(safe_read_text(editor_asmdef))
            asm["references"] = []
            safe_write_text(editor_asmdef, json.dumps(asm, indent=2, ensure_ascii=False) + "\n")

    # -------------------------
    # Step 4: Replace content tokens in all text files
    # -------------------------
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
        # Không replace trong wizard để tránh tự thay đổi/bug
        if f.name == "setup_wizard.py":
            continue
        if replace_in_file(f, replacements):
            changed += 1

    # -------------------------
    # Step 5: Rename folder path Template -> ModuleName (best-effort)
    # - Runtime: Runtime/HTDA/Framework/Template -> Runtime/HTDA/Framework/<ModuleName>
    # - Editor : Editor/HTDA/Framework/Template -> Editor/HTDA/Framework/<ModuleName>
    # - Legacy : Editor/HTDA/Template -> Editor/HTDA/Framework/<ModuleName> (phòng trường hợp cũ)
    # -------------------------
    rename_path_if_exists(
        pkg_root / "Runtime" / "HTDA" / "Framework" / "Template",
        pkg_root / "Runtime" / "HTDA" / "Framework" / cfg.module_name
    )
    rename_path_if_exists(
        pkg_root / "Editor" / "HTDA" / "Framework" / "Template",
        pkg_root / "Editor" / "HTDA" / "Framework" / cfg.module_name
    )
    rename_path_if_exists(
        pkg_root / "Editor" / "HTDA" / "Template",
        pkg_root / "Editor" / "HTDA" / "Framework" / cfg.module_name
    )

    # -------------------------
    # Step 6: Final output
    # -------------------------
    print("\n✅ HTDA Framework package initialized!")
    print(f"- Package: {new_package_id}")
    print(f"- Namespace: {new_ns_root}")
    if cfg.package_type == "runtime-only":
        print(f"- Assemblies: {new_asm_runtime}")
    elif cfg.package_type == "editor-only":
        print(f"- Assemblies: {new_asm_editor} (Editor-only)")
    else:
        print(f"- Assemblies: {new_asm_runtime}, {new_asm_editor}")
    print(f"- Repo (suggested): {repo_name}")
    print(f"- Updated files: {changed}\n")

    # Optional: self-destruct
    remove = prompt("Delete this setup wizard now? (y/N)", "N")
    if normalize_yes_no(remove):
        delete_path(Path(__file__).resolve())
        print("🧹 Wizard deleted.")


def main() -> None:
    # pkg_root = package root (Tools/..)
    pkg_root = Path(__file__).resolve().parents[1]

    # 1) Collect input
    cfg = collect_config_interactive()

    # 2) Confirm + optional edit loop
    cfg = confirm_and_edit(cfg)

    # 3) Apply changes
    apply_setup(pkg_root, cfg)


if __name__ == "__main__":
    main()