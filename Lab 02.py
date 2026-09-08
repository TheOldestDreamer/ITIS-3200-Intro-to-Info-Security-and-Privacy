import hashlib
import json
import os
from pathlib import Path, PureWindowsPath


def hash_file(file_path, algorithm="sha256"):
    hasher = hashlib.new(algorithm)
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (PermissionError, FileNotFoundError) as e:
        print(f"Error reading file {file_path}: {e}")
        return None


def traverse_directory(dir_path):
    hash_dict = {}

    clean_path_str = dir_path.strip().strip('"\'')
    directory = Path(clean_path_str).resolve()

    if not directory.exists() or not directory.is_dir():
        print(f"Invalid directory path: '{clean_path_str}'")
        return None

    for file_path in directory.rglob("*"):
        if file_path.is_file():
            file_hash = hash_file(file_path)
            if file_hash:
                win_path = str(PureWindowsPath(file_path.resolve()))
                hash_dict[win_path] = file_hash

    return hash_dict


def generate_table(dir_path, output_json="hashes.json"):
    print("Hashing files in Windows directory...")
    hash_data = traverse_directory(dir_path)

    if hash_data is None:
        return

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(hash_data, f, indent=4)

    print(f"Hash table generated and saved to {output_json}.")


def validate_hash(json_file="hashes.json"):
    json_path = Path(json_file.strip().strip('"\'')).resolve()

    if not json_path.exists():
        print(
            f"Error: Hash file '{json_path}' not found. Please generate a table first."
        )
        return

    if json_path.is_dir():
        print(
            f"Error: '{json_path}' is a directory, not a JSON file. Please provide the full path to your JSON file."
        )
        return

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            stored_hashes = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return

    if not stored_hashes:
        print("Stored hash table is empty.")
        return

    saved_paths = list(stored_hashes.keys())
    
    try:
        common_root = os.path.commonpath(saved_paths)
        base_dir = Path(common_root)
    except ValueError:
        print("Error: Paths in JSON span across different drives or invalid roots.")
        return

    current_hashes = {}
    if base_dir.exists():
        search_dir = base_dir if base_dir.is_dir() else base_dir.parent
        for file_path in search_dir.rglob("*"):
            if file_path.is_file():
                win_path = str(PureWindowsPath(file_path.resolve()))
                current_hashes[win_path] = hash_file(file_path)

    print("\n Hash Verification Results ")

    for filepath, stored_hash in stored_hashes.items():
        if filepath not in current_hashes:
            print(f"[Deleted] File missing: {filepath}")
        else:
            current_hash = current_hashes[filepath]
            if current_hash == stored_hash:
                print(f"[Valid]   {filepath} hash is valid.")
            else:
                print(f"[Invalid] {filepath} hash is INVALID.")

    for filepath in current_hashes:
        if filepath not in stored_hashes:
            print(f"[New] New file detected: {filepath}")


def main():
    print("File Hash Generator & Verifier")
    print("1. Generate a new hash table")
    print("2. Verify hashes")

    choice = input("Select an option (1 or 2): ").strip()

    if choice == "1":
        dir_path = input("Enter Windows directory path like C:\\Docs\\Notes or C:/Docs/Notes: ")
        generate_table(dir_path)

    elif choice == "2":
        json_file = (
            input(
                "Enter hash JSON path (press Enter for default 'hashes.json'): "
            ).strip()
            or "hashes.json"
        )
        validate_hash(json_file)

    else:
        print("Invalid choice. Gotta restart the program bozo.")


if __name__ == "__main__":
    main()