# config.py

import logging
from logging.config import dictConfig


def configure_logging():
    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }
        },
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })

    # Optional: Set Werkzeug logging to ERROR only to reduce noise
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
