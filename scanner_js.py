#!/usr/bin/python3

import os
import re
import help.fwork as fwork
import logging

logging.basicConfig(
    format='%(message)s',
    level=logging.DEBUG,
    # filename='scan.log'
)

suspected_js = {
    "js redirect 1": r";;function\s+(?P<fname>\w+)\(\)\{.*\}(?P=fname)\(\)===!0&&\(.+\);",
}


def check_js_file(filename):
    with open(filename, 'r') as tested_file:
        content = tested_file.read()

    for sig_name, js_regex in suspected_js.items():
        evil_js = re.compile(js_regex)
        match = evil_js.search(content)

        if match:
            logging.warning('found "%s" in file "%s"' % (sig_name, filename))
            clean_js = evil_js.sub('', content)

            # rename infected file
            os.rename(filename, filename + ".bak")
            fname = os.path.split(filename)[1]
            logging.warning('infected file "%s" renamed to "%s"' % (fname, fname + ".bak"))

            with open(filename, 'w') as clean_file:
                clean_file.write(clean_js)


if __name__ == '__main__':
    js_files = fwork.get_files_list(os.path.abspath(os.getcwd()), '*.js')

    for js_file in js_files:
        check_js_file(js_file)
