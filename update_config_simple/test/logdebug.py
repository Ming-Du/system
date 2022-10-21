#!/usr/bin/env python
import logging

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d]' '- %(levelname)s: %(message)s',
                    level=logging.INFO)
logging.info('debug message')
