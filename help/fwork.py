import fnmatch
import os
import help.wordpress


def get_files_list(path, mask):
    match_files = []
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, mask):
            file_path = os.path.join(root, filename)

            if os.path.isfile(file_path):
                match_files.append(file_path)

    return match_files


def get_dirs_list(path):
    dirs = [path]
    for root, dirnames, filenames in os.walk(path):
        if dirnames:
            dirs.extend(
                map(lambda d: os.path.join(root, d), dirnames)
            )

    return dirs


def files_exists(path, rel_path_files):
    if os.path.isdir(path):
        files = [os.path.join(path, f) for f in rel_path_files]
        return all(os.path.isfile(f) for f in files)
    return False


if __name__ == '__main__':
    cwd = os.getcwd()
    # print('files:')
    # print(get_files_list(dir, '*.py'))
    #
    updir = os.path.split(cwd)[0]
    print('updir: ', updir)
    # print('dirs:')
    # print(get_dir_list(updir[0]))

    # print(files_exists('c:\\Users\\admin\\Desktop\\sites\\140716 moving\\makememory\\docs', wp_fingerprint))
    # print(get_dirs_list('c:\\Users\\admin\\Desktop\\sites\\140716 moving\\makememory\\docs'))
    dir_list = get_dirs_list('c:\\Users\\admin\\Desktop\\sites\\110716')
    print('dirs: ', len(dir_list))

    for cur_dir in dir_list:
        # if files_exists(cur_dir, wp.wp_files):
        #     print(cur_dir, 'is wp root')
        #     print('wp_version:', wp.get_wp_version(cur_dir))
        if help.wordpress.WordpressEngine.check(path=cur_dir):
            print('WP root:', cur_dir)

