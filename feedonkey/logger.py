import logging
import os.path

from feedonkey.config import CONFIG_DIR

#--- log config ----------------------------------------------

"""create log object"""
logging.basicConfig(
        filename=os.path.join(CONFIG_DIR, 'feed-donkey.log'),
        level=logging.DEBUG,
        format='%(levelname)s [%(asctime)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
)

log=logging.getLogger('feed-donkey')


