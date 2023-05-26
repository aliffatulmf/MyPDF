import os
from tqdm import tqdm

def remove_all_items(folder_location, dry_run=False):
    """
    Removes all folders or files inside the specified folder location.

    Args:
        folder_location (str): The location of the folder.
        dry_run (bool, optional): If True, only displays the process without deleting any folder or file.
            Defaults to False.
    """
    if not os.path.isdir(folder_location):
        print("Invalid folder location.")
        return

    if dry_run:
        print("Dry run mode enabled. No items will be deleted.")

    items = os.listdir(folder_location)
    total_items = len(items)
    progress_bar = tqdm(total=total_items, desc="Processing", unit="item(s)")

    for item in items:
        item_path = os.path.join(folder_location, item)
        if not dry_run:
            if os.path.isfile(item_path):
                os.remove(item_path)
            else:
                os.rmdir(item_path)

        progress_bar.update(1)

    progress_bar.close()
    print("All items removed successfully.")

