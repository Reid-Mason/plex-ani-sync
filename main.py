import logging
import os
import sys
import time

import coloredlogs
import schedule
from anilist import Anilist
from plexConnection import PlexConnection

logger = logging.getLogger(__name__)
coloredlogs.install(level = 'DEBUG', fmt = '%(asctime)s [%(name)s] %(message)s', logger = logger)


def do_sync(retry: bool = True) -> None:
    """ Handles the execution of the main syncing function.

    :param retry: Whether or not to retry the sync if it fails.
    :return: None
    """
    try:
        from syncHandler import start_sync
        start_sync()

    # These errors can be fixed without restarting the docker container
    except PlexConnection.PlexServerUnreachable as e:
        logger.error(e)

    # These errors can only be fixed by changing data and restarting the docker container so the program should end
    except Anilist.InvalidToken and PlexConnection.InvalidPlexToken as e:
        logger.error(e)
        sys.exit()

    # Catch random errors to prevent the docker container stopping
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        if retry:
            logger.info("Retrying now")
            do_sync(retry = False)


if __name__ == '__main__':
    # Schedule the sync to run at the specified time
    sync_time = os.environ.get('sync_time')
    schedule.every().day.at(sync_time).do(lambda: do_sync())
    # Run the sync initially when the program starts
    do_sync()

    # Keep waiting for the time when the sync should occur
    while True:
        schedule.run_pending()
        time.sleep(60)
