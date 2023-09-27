import difflib
import filecmp
import os
import shutil


def diff_files(file_path_1, file_path_2):
    lines = []
    try:
        with open(file_path_1) as file_1:
            file_1_text = [x.lower() for x in file_1.readlines()]

        with open(file_path_2) as file_2:
            file_2_text = [x.lower() for x in file_2.readlines()]

        for line in difflib.unified_diff(
                file_1_text, file_2_text, fromfile=file_path_1,
                tofile=file_path_2, lineterm=''):
            if line.startswith("+") or line.startswith("-"):
                lines.append(line)
    except UnicodeDecodeError:
        # might be an image, or some other binary file.
        if open(file_path_1, "rb").read() != open(file_path_2, "rb").read():
            lines.append("Binary files are different")

    lines = [x for x in lines if
             "please remove" not in x
             and "<img src=\"http://geo.yahoo.com/serv?s=" not in x
             and "script language=\"javascript\" src=\"" not in x
             and "E:\\" not in x
             ]
    return lines


'''
Compare the contents of a site in the original location to the contents of the same site in the backup location.
Moves any new content from the backup to the original location. This function uses print statements instead of logging 
so output won't be out of order when combined with comparision printouts from filecmp and user input prompts.
'''
def compare_site_to_backup(original_location, backup_location, site_id):
    original_site_path = os.path.join(original_location, site_id)
    backup_site_path = os.path.join(backup_location, site_id)

    # if we can't find the backup dir, there's been a problem
    if not os.path.exists(backup_site_path):
        raise Exception(f"Backup site {backup_site_path} does not exist!")

    # if we cannot find a matching dir in the original location, we can copy the entire
    # backup dir contents to the original location
    if not os.path.exists(original_site_path):
        print(f"'{original_site_path}' does not exist. Copying all backup content from '{backup_site_path}' to "
              f"'{original_location}'")
        shutil.move(backup_site_path, original_location)
        return

    # otherwise compare the two directories and copy over any missing content
    comparison = filecmp.dircmp(original_site_path, backup_site_path)

    # if there are no differences found between the two directories, log that and delete the backup directory
    if len(comparison.left_only) == 0 and len(comparison.right_only) == 0 and len(comparison.diff_files) == 0:
        print(f"Blogs are identical in both directories. Removing the backup at '{backup_site_path}'")
        shutil.rmtree(backup_site_path)
        return

    # otherwise, there are differences between the original directory and backup to process
    print(f"Found differences between the two directories:")
    comparison.report_full_closure()

    # disambiguate between files with the same name but different content
    if len(comparison.diff_files) > 0:
        print(f"Found files with the same name but differing content! {comparison.diff_files}")
        for diff_file in comparison.diff_files:
            print(f"File {diff_file} exists in both directories but has different content")
            original_file = os.path.join(original_site_path, diff_file)
            backup_file = os.path.join(backup_site_path, diff_file)
            important_difference = diff_files(original_file, backup_file)
            if important_difference:
                print("Important differences found:")
                for line in important_difference:
                    print(f"\t{line}")
                discard = None
                if important_difference[0] == "Binary files are different":
                    discard = 'n'   # automatically keep different binary files
                while discard not in ['y', 'n']:
                    discard = input("Discard file from backup? (y/n)")
                if discard == 'y':
                    print(f"Deleting {diff_file} from {backup_site_path}")
                    os.remove(backup_file)
                else:
                    name, ext = os.path.splitext(diff_file)
                    new_name = f"{name}_frombackup{ext}"
                    print(f"Renaming file to {new_name} and relocating")
                    shutil.copy(backup_file, os.path.join(original_site_path, new_name))
                    os.remove(backup_file)

    #  if the right (backup) blog has new content, transfer it over
    if len(comparison.right_only) > 0:
        print("New content found in backup blog!")
        for backup_only_file in comparison.right_only:
            backup_path = os.path.join(backup_site_path, backup_only_file)
            print(f"copying {backup_path} to {original_site_path}")
            shutil.move(backup_path, original_site_path)

    # this doesn't really matter - just log for curiosity's sake.
    if len(comparison.left_only) > 0:
        print("Regular blog also has content not seen in backup blog!")
    else:
        print("All content in regular blog is also in backup blog!")

    # remove the backup directory
    shutil.rmtree(backup_site_path)
