#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    try:
        import local_settings
        settings_module = 'local_settings'
    except ImportError:
        settings_module = 'settings'
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
