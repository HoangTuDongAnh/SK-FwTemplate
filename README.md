# HTDA Framework Template (UPM)

This repository is a **Unity Package Manager (UPM) template** for creating new HTDA Framework modules.

## Quick start

1. Copy this folder as a new repository (recommended repo name: `HTDA-Framework-<ModuleName>`).
2. Run the wizard:

```bash
python Tools/setup_wizard.py
```

3. The wizard will:
- rename package id (com.htda.framework.<suffix>)
- rename assemblies and namespaces (HTDA.Framework.<ModuleName>)
- optionally remove Runtime or Editor parts based on package type

## Conventions

- Package id: com.htda.framework.<suffix> (e.g. core, editor.tools, patterns.pooling)

- Assembly: HTDA.Framework.<ModuleName> and HTDA.Framework.<ModuleName>.Editor

- Namespace root: HTDA.Framework.<ModuleName>

## Notes

- Keep Core packages small and stable.

- Move optional utilities/patterns/extensions into separate modules.

