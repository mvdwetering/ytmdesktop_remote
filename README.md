# YouTube Music Desktop Remote Control

Custom integration for Home Assistant to remote control the [YouTube Music Desktop app](https://ytmdesktop.app/).

> This integration currently only supports YTMDv1. Adding YTMDv2 support is something I would like to do at some point, but no idea when.

## Features

Exposes a mediaplayer to control a YouTube Music Desktop instance with the following features:

* Volume and mute
* Show metadata like artist, album, song and albumart
* Control playback (play, pause, next, prev, etc...)
* Set repeat mode

## Installation

### Home Assistant Community Store (HACS)

*Recommended because you get notified of updates.*

HACS is a 3rd party downloader for Home Assistant to easily install and update custom integrations made by the community. More information and installation instructions can be found on their site https://hacs.xyz/

* Add this repository `https://github.com/mvdwetering/ytmdesktop_remote` to HACS as a "custom repository" with category "integration"
* Add integration within HACS (use the + button and search for "YouTube Music Desktop Remote Control")
* Restart Home Assistant
* Go to the Home Assistant integrations menu and press the Add button and search for "YouTube Music Desktop Remote Control"

### Manual

* Install the custom component by downloading it and copy it to the `custom_components` directory as usual.
* Restart Home Assistant
* Go to the Home Assistant integrations menu and press the Add button and search for "YouTube Music Desktop Remote Control"
