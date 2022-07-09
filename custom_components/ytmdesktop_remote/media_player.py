from __future__ import annotations
from datetime import timedelta
from typing import List, Optional, Type

import aioytmdesktopapi

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerDeviceClass,
)
from homeassistant.components.media_player.const import (
    MEDIA_TYPE_MUSIC,
    REPEAT_MODE_ALL,
    REPEAT_MODE_OFF,
    REPEAT_MODE_ONE,
)
from homeassistant.config_entries import ConfigEntry, ConfigEntryAuthFailed
from homeassistant.const import (
    STATE_IDLE,
    STATE_PLAYING,
    STATE_PAUSED,
)
from homeassistant.util.dt import utcnow

from .const import DOMAIN, LOGGER

SUPPORTED_MEDIAPLAYER_COMMANDS = (
    MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.PREVIOUS_TRACK
    | MediaPlayerEntityFeature.REPEAT_SET
    # | MediaPlayerEntityFeature.SEEK     API command not working, see https://github.com/ytmdesktop/ytmdesktop/issues/885
)

SCAN_INTERVAL = timedelta(seconds=1)


async def async_setup_entry(hass, config_entry: ConfigEntry, async_add_entities):

    api = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([YtmDesktopMediaPlayer(config_entry.entry_id, api)], True)


class YtmDesktopMediaPlayer(MediaPlayerEntity):
    """YouTube Music Desktop mediaplayer."""

    _attr_should_poll = True
    _attr_media_image_remotely_accessible = True
    _attr_name = "YouTube Music Desktop"  # API does not expose a name. Pick a decent default, user can change

    def __init__(self, device_id: str, api: aioytmdesktopapi.YtmDesktop) -> None:
        self._api = api
        self._available = False
        self._position = None
        self._position_updated_at = None

        self._attr_unique_id = device_id
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
        }

    async def async_update(self) -> None:
        """Do a request to the YouTube Music Desktop instance"""
        try:
            await self._api.update()
            self._available = True

            if (
                self._api.player
                and self._position != self._api.player.seekbar_current_position
            ):
                self._position = self._api.player.seekbar_current_position
                self._position_updated_at = utcnow()
        except aioytmdesktopapi.RequestError:
            LOGGER.debug("ConnectionError for %s", self._api.host)
            self._available = False
        except aioytmdesktopapi.Unauthorized as err:
            LOGGER.error("Authentication error for %s", self._api.host)
            self._available = False
            raise ConfigEntryAuthFailed(err) from err

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> str:
        """Return the state of the entity."""
        if not self._api.player or not self._api.player.has_song:
            return STATE_IDLE
        if self._api.player.is_paused:
            return STATE_PAUSED
        return STATE_PLAYING

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        return self._api.player.volume_percent / 100

    @property
    def supported_features(self):
        """Flag of media commands that are supported."""
        return SUPPORTED_MEDIAPLAYER_COMMANDS

    async def async_set_volume_level(self, volume) -> None:
        """Set volume level, convert range from 0..1."""
        await self._api.send_command.player_set_volume(volume * 100)

    async def async_volume_up(self) -> None:
        """Volume up media player."""
        await self._api.send_command.player_volume_up()

    async def async_volume_down(self) -> None:
        """Volume down media player."""
        await self._api.send_command.player_volume_down()

    async def async_media_play(self) -> None:
        await self._api.send_command.track_play()

    async def async_media_pause(self) -> None:
        await self._api.send_command.track_pause()

    async def async_media_next_track(self) -> None:
        await self._api.send_command.track_next()

    async def async_media_previous_track(self) -> None:
        await self._api.send_command.track_previous()

    async def async_media_seek(self, position) -> None:
        if self._api.track:
            LOGGER.warning("position: %d", position)
            await self._api.send_command.player_set_seekbar(int(position))

    @property
    def repeat(self) -> Optional[str]:
        """Return current repeat mode."""
        if self._api.player.repeat_type == aioytmdesktopapi.RepeatType.ONE:
            return REPEAT_MODE_ONE
        if self._api.player.repeat_type == aioytmdesktopapi.RepeatType.ALL:
            return REPEAT_MODE_ALL
        if self._api.player.repeat_type == aioytmdesktopapi.RepeatType.NONE:
            return REPEAT_MODE_OFF
        return None

    async def async_set_repeat(self, repeat) -> None:
        """Set repeat mode."""
        if repeat == REPEAT_MODE_ALL:
            await self._api.send_command.player_repeat(aioytmdesktopapi.RepeatType.ALL)
        elif repeat == REPEAT_MODE_OFF:
            await self._api.send_command.player_repeat(aioytmdesktopapi.RepeatType.NONE)
        elif repeat == REPEAT_MODE_ONE:
            await self._api.send_command.player_repeat(aioytmdesktopapi.RepeatType.ONE)

    # Media info
    @property
    def media_content_type(self) -> Optional[str]:
        """Content type of current playing media."""
        return MEDIA_TYPE_MUSIC

    @property
    def media_title(self) -> Optional[str]:
        """Title of current playing media."""
        return self._api.track.title if self._api.track else None

    @property
    def media_artist(self) -> Optional[str]:
        """Artist of current playing media, music track only."""
        return self._api.track.author if self._api.track else None

    @property
    def media_album_name(self) -> Optional[str]:
        """Album name of current playing media, music track only."""
        return self._api.track.album if self._api.track else None

    @property
    def media_image_url(self) -> Optional[str]:
        """Image url of current playing media."""
        return self._api.track.cover if self._api.track else None

    @property
    def media_position(self):
        """Position of current playing media in seconds."""
        return self._position

    @property
    def media_position_updated_at(self):
        """When was the position of the current playing media valid.

        Returns value from homeassistant.util.dt.utcnow().
        """
        if self.state == STATE_PLAYING:
            return self._position_updated_at

    @property
    def media_duration(self):
        """Time in seconds of current song duration."""
        return self._api.track.duration if self._api.track else None
