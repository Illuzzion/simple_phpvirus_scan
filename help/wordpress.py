#!/usr/bin/python3

import os
import re
import help.engine as engine
import help.fwork


class WordpressEngine(engine.WebEngine):
    wp_files = ['index.php', 'wp-config.php', 'wp-login.php',
                # в wp-settings.php есть define( 'WPINC', 'wp-includes' );
                # 'wp-settings.php',
                'wp-admin' + os.path.sep + 'setup-config.php',
                # если в wp-settings.php 'WPINC' = 'wp-includes'
                # то в wp-includes/version.php есть версия wordpress
                # 'wp-includes/version.php'
                ]
    version = None

    def __init__(self, root_path):
        super().__init__("Wordpress")
        self.data = dict(root=root_path)

    @classmethod
    def check(cls, path):
        return help.fwork.files_exists(path, cls.wp_files)

    def get_version(self):
        if self.data.get('version'):
            return self.data['version']

        try:
            wp_settings_path = os.path.join(self.data['root'], 'wp-settings.php')
            with open(wp_settings_path) as f:
                settings_content = f.read()

            wp_inc_re = r"define\s*\(\s*[\''\"]WPINC[\''\"]\s*,\s*[\''\"](.+)[\''\"]\s*\)"
            wp_inc_path = re.search(wp_inc_re, settings_content)

            if wp_inc_path:
                wp_inc_path = wp_inc_path.group(1)
                self.data['wpinc'] = wp_inc_path
                wp_version_path = os.path.join(self.data['root'], wp_inc_path, 'version.php')

                if os.path.isfile(wp_version_path):
                    # print('version path:', wp_version_path)
                    with open(wp_version_path) as f:
                        version_content = f.read()

                    wp_version_re = r"\$wp_version\s*=\s*[\'\"](.+)[\'\"]"
                    wp_version = re.search(wp_version_re, version_content)

                    if wp_version:
                        wp_version = wp_version.group(1)
                        self.data['version'] = wp_version
                        return wp_version
        except Exception as e:
            print(e)


if __name__ == "__main__":
    # wp = WordpressEngine()
    # print(wp.name)

    dir_list = help.fwork.get_dirs_list('c:\\Users\\admin\\Desktop\\sites\\110716')
    print('dirs: ', len(dir_list))

    for cur_dir in dir_list:
        if WordpressEngine.check(cur_dir):
            wp_inst = WordpressEngine(cur_dir)
            print(wp_inst.data)
            print('version:', wp_inst.get_version())
            print('2version:', wp_inst.get_version())
