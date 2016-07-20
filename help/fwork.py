import fnmatch
import os


def get_files_list(path, mask):
    match_files = []
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, mask):
            file_path = os.path.join(root, filename)

            if os.path.isfile(file_path):
                match_files.append(file_path)

    return match_files
