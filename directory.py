import os

from tqdm import tqdm

class DirectoryError:
    pass

def clean_directory(folder_path: str, dry_run: bool = False):
    if not os.path.exists(folder_path):
        raise DirectoryError(f"Error: {folder_path} does not exist.")

    parent_dir = os.path.basename(folder_path)
    total_files = os.listdir(folder_path)

    if len(total_files) == 0:
        print(f"Folder {parent_dir} already cleaned.")
        return

    for entry in tqdm(total_files, desc="Removing files"):
        if os.path.isfile(os.path.join(folder_path, entry)):
            if not dry_run:
                os.remove(os.path.join(folder_path, entry))

    print(f"Cleaning {parent_dir} folder completed.")
    return total_files
