"""Constants for the YouTube Music Desktop Remote Control integration."""
from datetime import timedelta
import logging

DOMAIN = "ytmdesktop_remote"

LOGGER = logging.getLogger(__package__)


# Using timedelta of 5 seconds often gives Server Disconnect exceptions
# maybe YTMD has a 5 second timeout that conflicts occasionally?
COORDINATOR_UPDATE_INTERVAL = timedelta(seconds=6)
