"""Fixtures for testing."""
from typing import Callable, NamedTuple, Type
from unittest.mock import DEFAULT, Mock, create_autospec, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry

from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    mock_device_registry,
)


import custom_components.ytmdesktop_remote as ytmdesktop_remote


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield
