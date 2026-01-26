# HTDA – Unity Package Starter Kit 📦

![Unity](https://img.shields.io/badge/Unity-6000%2B-000000?logo=unity)
![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

A robust starter template for creating **Unity Packages** within the **HoangTuDongAnh** ecosystem.

This repository is designed to be used as a **GitHub Template**. It includes a pre-configured folder structure (`Runtime` & `Editor`), assembly definitions, and a powerful **Python Setup Wizard** to automate the initialization of new modules.

---

## ✨ Features

* **Standard UPM Structure:** Ready-to-use `Runtime` and `Editor` folders with Assembly Definitions (`.asmdef`).
* **Automated Setup:** A Python script (`setup_wizard.py`) that handles:
    * Renaming `package.json` fields (name, displayName, urls).
    * Renaming `.asmdef` files and their internal References.
    * Refactoring C# Namespaces (e.g., `HoangTuDongAnh.UP.Template` → `HoangTuDongAnh.UP.YourSystem`).
    * Self-destruction after setup is complete.
* **Git Ready:** properly configured `.gitignore` for Unity Packages.

---

## 🚀 Getting Started

### 1. Create Your Repository
DO NOT clone this repository directly. Instead:
1.  Click the **Use this template** button at the top of this page.
2.  Name your new repository (e.g., `UP-Audio-System`, `UP-Network`).
3.  Create the repository.

### 2. Prepare Development Environment
To develop a package, you need a hosting Unity Project (a sandbox).
1.  Open or create a standard Unity Project (e.g., `MySandboxProject`).
2.  Navigate to the `Packages` folder of that project via terminal:
    ```bash
    cd path/to/MySandboxProject/Packages
    ```

### 3. Clone Your New Repository
Clone the repository you created in Step 1 into the `Packages` folder.
*Tip: It is recommended to rename the folder to match the package name conventions.*

```bash
# Syntax: git clone <your-new-repo-url> <folder-name>
git clone [https://github.com/YourUsername/UP-Audio-System.git](https://github.com/YourUsername/UP-Audio-System.git) com.hoangtudonganh.up-audio
```

### 4. Run Setup Wizard
Enter the package folder and run the automation script:

```bash
cd com.hoangtudonganh.up-audio
python setup_wizard.py
```

Follow the on-screen prompts:

1. Package Name: Enter the short name (e.g., audio).

2. Display Name: Enter the formatted name (e.g., Audio System).

3. Confirm: The script will rename all namespaces, files, and configurations automatically.

### 5. Verify in Unity

1. Return to the Unity Editor.

2. Unity will refresh and import the new package.

3. Open Window > Package Manager → In Project.

4. You should see HTDA – UP Audio System listed and ready for development.

---

## 📂 Folder Structure
After running the wizard, your structure will look like this (example for Audio System):

```plaintext
com.hoangtudonganh.up-audio/
├── Editor/
│   └── HoangTuDongAnh.UP.AudioSystem.Editor.asmdef  <-- Auto-referenced to Runtime
├── Runtime/
│   └── HoangTuDongAnh.UP.AudioSystem.asmdef         <-- Main assembly
├── .gitignore
├── LICENSE.md
├── README.md
└── package.json                                     <-- Auto-updated metadata
```

---

## 🛠 Manual Configuration (Optional)
If you do not wish to use the Python wizard, you must manually:

1. Rename .asmdef files in Runtime and Editor.

2. Open .asmdef files and update the "name", "rootNamespace", and "references" fields.

3. Update package.json with your specific module details.

---

## 📜 License
This project is licensed under the MIT License. See [LICENSE.md](LICENSE.md) for details.