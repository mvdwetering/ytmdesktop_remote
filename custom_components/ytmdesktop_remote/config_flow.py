"""Config flow for YouTube Music Desktop Remote Control integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol  # type: ignore[import]

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

import aioytmdesktopapi

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("host"): str,
        vol.Optional("password"): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """
    Validate the user input allows us to connect.
    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    try:
        async with aioytmdesktopapi.YtmDesktop(
            async_get_clientsession(hass), data["host"], data.get("password", None)
        ) as api:
            await api.initialize()

            # There is no explicit way to check if authenticated.
            # Only commands need to have authentication so lets send a dummy command
            # Turns out Play and Pause are both toggles, so send it twice
            # to get the player back in the same state :/
            await api.send_command.track_pause()
            await api.send_command.track_pause()
    except aioytmdesktopapi.Unauthorized:
        raise InvalidAuth
    except aioytmdesktopapi.RequestError:
        raise CannotConnect

    # Return info that you want to store in the config entry.
    return {"title": "YouTube Music Desktop"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for YouTube Music Desktop Remote Control."""

    VERSION = 1

    reauth_entry: config_entries.ConfigEntry | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            if self.reauth_entry:
                self.hass.config_entries.async_update_entry(
                    self.reauth_entry, data=user_input
                )
                await self.hass.config_entries.async_reload(self.reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")

            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                STEP_USER_DATA_SCHEMA, user_input
            ),
            errors=errors,
        )

    async def async_step_reauth(self, user_input=None):
        """Perform reauth upon an API authentication error."""
        self.reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )

        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                last_step=False,
            )

        assert self.reauth_entry is not None
        return await self.async_step_user(self.reauth_entry.data)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
