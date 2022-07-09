# YouTube Music Desktop Remote Control

Custom integration for Home Assistant to remote control the [YouTube Music Desktop app](https://ytmdesktop.app/).

Status:

* Mediaplayer seems to work fine
* Unittests not done yet
* `aioytmdesktopapi` dependency not available on PyPi yet, so need to install manually

## Features

Exposes a mediaplayer to control a YouTue Music Desktop instance with the following features:

* Volume and mute
* Show metadata like artist, album, song
* Control playback (play, pause, next, prev, etc...)
* Set repeat mode

## Installation

### HACS

* Add this repository `https://github.com/mvdwetering/ytmdesktop_remote` to HACS as a "custom repository" with category "integration"
* Add integration within HACS (use the + button and search for "YouTube Music Desktop Remote Control")
* Restart Home Assistant
* Go to the Home Assistant integrations menu and press the Add button and search for "YouTube Music Desktop Remote Control"

### Manual

* Install the custom component by downloading it and copy it to the `custom_components` directory as usual.
* Restart Home Assistant
* Go to the Home Assistant integrations menu and press the Add button and search for "YouTube Music Desktop Remote Control"
