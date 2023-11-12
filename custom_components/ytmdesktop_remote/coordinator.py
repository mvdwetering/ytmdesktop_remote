"""Coordinator for the YouTube Music Desktop Remote Control integration."""

from dataclasses import dataclass
import datetime
import aioytmdesktopapi
import async_timeout

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util.dt import utcnow

from .const import COORDINATOR_UPDATE_INTERVAL, LOGGER


@dataclass
class CoordinatorData:
    api: aioytmdesktopapi.YtmDesktop
    last_updated: datetime.datetime


class YtmdCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, api: aioytmdesktopapi.YtmDesktop):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            LOGGER,
            # Name of the data. For logging purposes.
            name="YouTube Music Desktop Remote Control",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=COORDINATOR_UPDATE_INTERVAL,
            request_refresh_debouncer=Debouncer(
                hass, LOGGER, cooldown=1.0, immediate=False
            ),
        )
        self.api = api

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(2):
                if self.data is None:
                    await self.api.initialize()
                else:
                    await self.api.update()
                return CoordinatorData(self.api, utcnow())
        except aioytmdesktopapi.Unauthorized as err:
            # Raising ConfigEntryAuthFailed will cancel future updates
            # and start a config flow with SOURCE_REAUTH (async_step_reauth)
            raise ConfigEntryAuthFailed from err
        except aioytmdesktopapi.RequestError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    # async def async_update(self) -> None:
    #     """Do a request to the YouTube Music Desktop instance"""
    #     try:
    #         await self._api.update()
    #         self._available = True

    #         if (
    #             self._api.player
    #             and self._position != self._api.player.seekbar_current_position
    #         ):
    #             self._position = self._api.player.seekbar_current_position
    #             self._position_updated_at = utcnow()
    #     except aioytmdesktopapi.RequestError:
    #         if self._available:
    #             LOGGER.error("Error updating %s", self._api.host)
    #         if LOGGER.level == logging.DEBUG:
    #             LOGGER.exception("Exception during update for %s" % self._api.host)

    #         self._available = False
    #     except aioytmdesktopapi.Unauthorized as err:
    #         LOGGER.error("Authentication error for %s", self._api.host)
    #         self._available = False
    #         raise ConfigEntryAuthFailed(err) from err
