#!/usr/bin/python3

import fnmatch
import os
import re
import logging

logging.basicConfig(
    format='%(message)s',
    level=logging.DEBUG,
    filename='scan.log'
)


def get_files_list(path, mask):
    match_files = []
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, mask):
            file_path = os.path.join(root, filename)

            if os.path.isfile(file_path):
                match_files.append(file_path)

    return match_files


def show_suspected_code(string, suspected_word):

    for rule in suspected_word:
        try:
            pos = string.index(rule)
            start_pos = 0
            end_pos = len(string)

            if (pos - 20) >= 0:
                start_pos = pos - 20

            if (pos + 30) <= end_pos:
                end_pos = pos + 30
            yield string[start_pos:end_pos].strip()

        except ValueError:
            pass


def check_spaces(string, max_len=400, max_spaces_percent=50):
    strlen = len(string)
    fresult = []

    if strlen > max_len:
        fresult = ['long_string']

        spaces_count = string.count(' ')
        spaces_percent = round(((spaces_count / strlen) * 100), 2)

        if spaces_percent >= max_spaces_percent:
            fresult.append('too_many_spaces')

    return fresult


def is_bad_code(string):
    rule_names = []
    # 'popen,exec,ftp_exec,system,passthru,get_current_user,proc_open,shell_exec,ini_restore,getmygid,dl,symlink,chgrp,ini_set,putenv,extension_loaded,getmyuid,fsockopen,posix_setuid,posix_setsid,posix_setpgid,posix_kill,apache_child_terminate,chmod,chdir,pcntl_exec,phpinfo,virtual,proc_close,proc_get_status,proc_terminate,proc_nice,proc_getstatus,proc_close,escapeshellcmd,escapeshellarg,show_source,pclose,safe_dir,dl,ini_restore,chown,chgrp,shown_source,mysql_list_dbs,get_current_user,getmyid,leak,pfsockopen'
    bad_words_regex = {
        'eval': r'([\s@;/]*)eval([\s]*)\(',
        'assert': r'([\s@;/]*)assert([\s]*)\(',
        'system': r'([\s@;/]*)system([\s]*)\(',
        'chmod': r'([\s@;/]*)chmod([\s]*)\(',
        'fileperms': r'([\s@;/]*)fileperms([\s]*)\(',
        'unlink': r'([\s@;/]*)unlink([\s]*)\(',
        'base64_decode': r'([\s@;/]*)base64_decode([\s]*)\(',

        'variable_as_function': r'(\$[\w\'\"\[\]]+)\((.*)\)',
    }
    # цикл пербора по подозрительным словам
    for rule_name, bad_word in bad_words_regex.items():
        c_bad_word = re.compile(bad_word)
        match = c_bad_word.search(string)

        if match:
            rule_names.append(rule_name)

    # проверим вхождение подстроки
    contains_substring = {
        'wso_shell': 'wso_version',
        'wso_shell': 'filesman',
        'curl_get_from_webpage_one_time': 'curl_get_from_webpage_one_time',
        'maybe_session_include': 'sys_get_temp_dir',
    }

    for rule_name, bad_word in contains_substring.items():
        if bad_word.lower() in string.lower():
            rule_names.append(rule_name)

    # проверим длину строки и процент пробелов
    rule_names.extend(check_spaces(string))

    return rule_names


def is_bad_filename(file_path):
    bad_file_names = [
        'adodb.class.php',
        'autoconf.php',
        'dump.php',
        'syslib.php',
        'editclass.php',
        'plugin.php',
        'db-update.php',
        'getFile.php'
    ]

    fname = os.path.split(file_path)[-1]
    for bfn in bad_file_names:
        if bfn == fname:
            return True


def check_file(filename):
    result_dict = {'lines': {}, 'lines_count': 0}

    if is_bad_filename(filename):
        result_dict['bad_filename'] = True

    with open(filename, 'r') as tested_file:
        try:
            for line_number, line in enumerate(tested_file):
                line_lower = line.lower()
                reasons = is_bad_code(line_lower)
                # reasons.extend(bad_code)

                if reasons:
                    line_dict = {'reason': reasons, 'content': line.strip(), 'suspected': []}

                    for code in show_suspected_code(line.strip(), reasons):
                        line_dict['suspected'].append(code)

                    result_dict['lines'][line_number] = line_dict

                result_dict['lines_count'] = line_number + 1

        except UnicodeDecodeError:
            pass

    return result_dict


if __name__ == '__main__':

    files_list = get_files_list(os.path.abspath(os.getcwd()), '*.php')
    logging.debug('Found {} files\n'.format(len(files_list)))
    files_results = {}

    for filename in files_list:
        result = check_file(filename=filename)

        if len(result['lines']) or result.get('bad_filename', False):
            files_results[filename] = result

    logging.debug("Suspected files: {}".format(len(files_results)))


    def sort_results(record):
        weight = 0
        data = record[1]

        weights = {
            'eval': 5,
            'variable_as_function': 1,
            'unlink': 1,
            'base64_decode': 5,
            'assert': 5,
            'chmod': 1,
            'long_string': 1,
            'too_many_spaces': 2,
            'system': 1,
            'fileperms': 1,
            'wso_shell': 50,
            'curl_get_from_webpage_one_time': 5,
            'maybe_session_include': 2,
        }

        for line in data['lines'].values():
            for reason in line['reason']:
                weight += weights[reason]

        if data.get('bad_filename', False):
            weight += 30

        return weight


    sorted_results = sorted(files_results.items(), key=sort_results, reverse=True)

    for record in sorted_results:
        logging.debug('file: "{}"'.format(record[0]))
        logging.debug('weight: {}'.format(sort_results(record)))

        line_items = sorted(record[1]['lines'].items())

        for line_number, data in line_items:
            logging.debug('\ton line: {} rule: "{}"'.format(line_number, ', '.join(data['reason'])))
            logging.debug('\t\tcode: {}'.format(data['content']))
            if data['suspected']:
                logging.debug('\t\t\tsuspected: {}'.format(data['suspected']))
            logging.debug('\n')
