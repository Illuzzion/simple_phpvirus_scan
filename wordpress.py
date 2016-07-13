#!/usr/bin/python3

wp_files = ['index.php', 'wp-config.php', 'wp-login.php',
            # в wp-settings.php есть define( 'WPINC', 'wp-includes' );
            'wp-settings.php',

            # если в wp-settings.php 'WPINC' = 'wp-includes'
            # то в wp-includes/version.php есть версия wordpress
            'wp-includes/version.php']

wp_dirs = ['wp-includes', 'wp-content', 'wp-admin']
