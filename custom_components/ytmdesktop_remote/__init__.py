"""The YouTube Music Desktop Remote Control integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_HOST, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from aioytmdesktopapi import YtmDesktop

from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up YouTube Music Desktop Remote Control from a config entry."""
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = YtmDesktop(
        async_get_clientsession(hass),
        entry.data[CONF_HOST],
        entry.data.get(CONF_PASSWORD, None),
    )

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
