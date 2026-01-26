import os
import json

# === CONFIGURATION ===
# These tokens must match the placeholders in your Template files
TEMPLATE_NAMESPACE = "HoangTuDongAnh.UP.Template"  # The namespace in your .asmdef/.cs files
TEMPLATE_TOKEN     = "Template"                    # The keyword in filenames to rename
PKG_TOKEN          = "up-name"                     # Token in package.json (name)
DISPLAY_TOKEN      = "<DisplayName>"               # Token in package.json (displayName)

def clear():
    """Clears the console screen."""
    os.system("cls" if os.name == "nt" else "clear")

def ask(prompt, required=True):
    """Helper to get user input."""
    while True:
        val = input(f">> {prompt}: ").strip()
        if val or not required:
            return val
        print("   ! This field is required.")

def replace_in_file(path, mapping):
    """Reads a file, replaces tokens based on mapping, and saves if changed."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        original_content = content
        for k, v in mapping.items():
            content = content.replace(k, v)
            
        if original_content != content:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
    except Exception as e:
        print(f"   [!] Error reading file {path}: {e}")
    return False

def main():
    clear()
    print("=== HTDA - UNITY PACKAGE SETUP WIZARD ===\n")

    # 1. Gather Information
    # Example: "audio" -> becomes "com.hoangtudonganh.up-audio"
    short_name = ask("Package Name (short, lowercase, e.g., 'audio', 'core')").lower()
    
    # Example: "Audio System" -> becomes "HTDA – UP Audio System"
    display_name = ask("Display Name (e.g., 'Audio System')")
    
    desc = ask("Description (optional)", required=False)

    # 2. Process Names
    # Remove spaces for Namespace/Filenames: "Audio System" -> "AudioSystem"
    pascal_name = display_name.replace(" ", "") 
    
    # Create Repo Name for URLs: "Audio System" -> "UP-Audio-System"
    repo_name = f"UP-{display_name.replace(' ', '-')}"

    # 3. Create Replacement Mapping
    mapping = {
        # package.json tokens
        PKG_TOKEN: short_name,
        DISPLAY_TOKEN: display_name,
        
        # Namespace in C# and Asmdef
        # e.g., HoangTuDongAnh.UP.Template -> HoangTuDongAnh.UP.AudioSystem
        TEMPLATE_NAMESPACE: f"HoangTuDongAnh.UP.{pascal_name}",
        
        # Repository URL token
        "UP-Template": repo_name
    }

    print("\n[Processing...]")

    # --- STEP 1: Update package.json ---
    pkg_json_path = "package.json"
    if os.path.exists(pkg_json_path):
        try:
            with open(pkg_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Update fields
            data["name"] = f"com.hoangtudonganh.up-{short_name}"
            data["displayName"] = f"HTDA – UP {display_name}"
            if desc:
                data["description"] = desc
            
            # Update URLs
            repo_url = f"https://github.com/HoangTuDongAnh/{repo_name}"
            data["documentationUrl"] = repo_url
            data["changelogUrl"] = f"{repo_url}/blob/main/CHANGELOG.md"
            data["licensesUrl"] = f"{repo_url}/blob/main/LICENSE.md"

            with open(pkg_json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("   [+] Updated package.json")
        except Exception as e:
            print(f"   [!] Failed to update package.json: {e}")
    else:
        print("   [!] package.json not found")

    # --- STEP 2: Replace Content in Files ---
    ignore_files = {"setup_wizard.py", "package.json", ".DS_Store"}
    target_exts = (".cs", ".asmdef", ".md", ".txt", ".json")

    for root, dirs, files in os.walk("."):
        if ".git" in root: continue 
        
        for file in files:
            if file in ignore_files: continue
            
            if file.endswith(target_exts):
                full_path = os.path.join(root, file)
                if replace_in_file(full_path, mapping):
                    pass # Content updated

    # --- STEP 3: Rename Files (Asmdef & Scripts) ---
    # Walk bottom-up to rename files before folders (if needed)
    renamed_count = 0
    for root, dirs, files in os.walk(".", topdown=False):
        if ".git" in root: continue

        for file in files:
            # Rename any file containing "Template" (e.g., the .asmdef files)
            if TEMPLATE_TOKEN in file: 
                old_path = os.path.join(root, file)
                
                # e.g., HoangTuDongAnh.UP.Template.asmdef -> HoangTuDongAnh.UP.AudioSystem.asmdef
                new_name = file.replace(TEMPLATE_TOKEN, pascal_name)
                new_path = os.path.join(root, new_name)
                
                try:
                    os.rename(old_path, new_path)
                    print(f"   [+] Renamed: {file} -> {new_name}")
                    renamed_count += 1
                except OSError as e:
                    print(f"   [!] Rename error for {file}: {e}")

    # --- FINISH ---
    print(f"\nSUCCESS: HTDA – UP {display_name} is ready!")
    print(f"Namespace: HoangTuDongAnh.UP.{pascal_name}")

    # Self-destruct option
    if ask("Delete this setup script? (y/n)", required=False).lower() == "y":
        try:
            os.remove(__file__)
            print("   [+] setup_wizard.py deleted.")
        except:
            print("   [!] Could not delete the script.")

if __name__ == "__main__":
    main()