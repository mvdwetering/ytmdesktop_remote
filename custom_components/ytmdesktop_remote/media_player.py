from __future__ import annotations
import asyncio
from typing import Optional

import aioytmdesktopapi

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
    RepeatMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER
from .coordinator import YtmdCoordinator

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


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
):
    coordinator: YtmdCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [YtmDesktopMediaPlayer(coordinator, config_entry.entry_id)], True
    )


class YtmDesktopMediaPlayer(CoordinatorEntity, MediaPlayerEntity):
    """YouTube Music Desktop mediaplayer."""

    _attr_media_image_remotely_accessible = True
    _attr_name = None
    _attr_has_entity_name = True

    def __init__(self, coordinator: YtmdCoordinator, configentry_id: str) -> None:
        super().__init__(coordinator)
        self.coordinator: YtmdCoordinator
        self._configentry_id = configentry_id

        self._attr_unique_id = configentry_id
        self._attr_device_info = {
            "name": "YouTube Music Desktop",  # API does not expose a name. Pick a decent default, user can change
            "identifiers": {(DOMAIN, configentry_id)},
        }

    def schedule_ha_update(func):
        async def _decorator(self: YtmDesktopMediaPlayer, *args, **kwargs):
            try:
                await func(self, *args, **kwargs)
                # Use request_async_refresh so the debouncer is used to delay the request a bit
                await self.coordinator.async_request_refresh()
            except aioytmdesktopapi.Unauthorized:
                entry = self.hass.config_entries.async_get_entry(self._attr_unique_id)
                entry.async_start_reauth(self.hass)
                # await self.hass.config_entries.async_reload(self._configentry_id)

        return _decorator

    @property
    def state(self) -> MediaPlayerState | None:
        """Return the state of the entity."""
        if not self.coordinator.api.player or not self.coordinator.api.player.has_song:
            return MediaPlayerState.IDLE
        if self.coordinator.api.player.is_paused:
            return MediaPlayerState.PAUSED
        return MediaPlayerState.PLAYING

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        return self.coordinator.api.player.volume_percent / 100

    @property
    def supported_features(self):
        """Flag of media commands that are supported."""
        return SUPPORTED_MEDIAPLAYER_COMMANDS

    @schedule_ha_update
    async def async_set_volume_level(self, volume) -> None:
        """Set volume level, convert range from 0..1."""
        await self.coordinator.api.send_command.player_set_volume(volume * 100)

    @schedule_ha_update
    async def async_volume_up(self) -> None:
        """Volume up media player."""
        await self.coordinator.api.send_command.player_volume_up()

    @schedule_ha_update
    async def async_volume_down(self) -> None:
        """Volume down media player."""
        await self.coordinator.api.send_command.player_volume_down()

    @schedule_ha_update
    async def async_media_play(self) -> None:
        await self.coordinator.api.send_command.track_play()

    @schedule_ha_update
    async def async_media_pause(self) -> None:
        await self.coordinator.api.send_command.track_pause()

    @schedule_ha_update
    async def async_media_next_track(self) -> None:
        await self.coordinator.api.send_command.track_next()

    @schedule_ha_update
    async def async_media_previous_track(self) -> None:
        await self.coordinator.api.send_command.track_previous()

    @schedule_ha_update
    async def async_media_seek(self, position) -> None:
        if self.coordinator.api.track:
            await self.coordinator.api.send_command.player_set_seekbar(int(position))

    @property
    def repeat(self) -> Optional[str]:
        """Return current repeat mode."""
        if self.coordinator.api.player.repeat_type == aioytmdesktopapi.RepeatType.ONE:
            return RepeatMode.ONE
        if self.coordinator.api.player.repeat_type == aioytmdesktopapi.RepeatType.ALL:
            return RepeatMode.ALL
        if self.coordinator.api.player.repeat_type == aioytmdesktopapi.RepeatType.NONE:
            return RepeatMode.OFF
        return None

    @schedule_ha_update
    async def async_set_repeat(self, repeat) -> None:
        """Set repeat mode."""
        if repeat == RepeatMode.ALL:
            await self.coordinator.api.send_command.player_repeat(
                aioytmdesktopapi.RepeatType.ALL
            )
        elif repeat == RepeatMode.OFF:
            await self.coordinator.api.send_command.player_repeat(
                aioytmdesktopapi.RepeatType.NONE
            )
        elif repeat == RepeatMode.ONE:
            await self.coordinator.api.send_command.player_repeat(
                aioytmdesktopapi.RepeatType.ONE
            )

    # Media info
    @property
    def media_content_type(self) -> Optional[str]:
        """Content type of current playing media."""
        return MediaType.MUSIC

    @property
    def media_title(self) -> Optional[str]:
        """Title of current playing media."""
        return self.coordinator.api.track.title if self.coordinator.api.track else None

    @property
    def media_artist(self) -> Optional[str]:
        """Artist of current playing media, music track only."""
        return self.coordinator.api.track.author if self.coordinator.api.track else None

    @property
    def media_album_name(self) -> Optional[str]:
        """Album name of current playing media, music track only."""
        return self.coordinator.api.track.album if self.coordinator.api.track else None

    @property
    def media_image_url(self) -> Optional[str]:
        """Image url of current playing media."""
        return self.coordinator.api.track.cover if self.coordinator.api.track else None

    @property
    def media_position(self):
        """Position of current playing media in seconds."""
        return (
            self.coordinator.api.player.seekbar_current_position
            if self.coordinator.api.player
            else None
        )

    @property
    def media_position_updated_at(self):
        """When was the position of the current playing media valid.

        Returns value from homeassistant.util.dt.utcnow().
        """
        if self.state == MediaPlayerState.PLAYING:
            return self.coordinator.data.last_updated

    @property
    def media_duration(self):
        """Time in seconds of current song duration."""
        return (
            self.coordinator.api.track.duration if self.coordinator.api.track else None
        )
