import logging
import sys
from django.core.management import call_command
from django.conf import settings

import atlasnode


def init():
    settings.configure(
        DATABASES = atlasnode.config['database'],
        INSTALLED_APPS = ('atlasnode.orm',),
    )

    logging.info('Preparing database')

    try:
        call_command('syncdb', interactive=False)
    except Exception as e:
        logging.error('Failed to initialize DB')
        logging.error(str(e))
        sys.exit(1)
