# Cumulus MX for Home Assistant

Custom integration for Cumulus MX via its local web tag API. Early release: tested by static checks only; please validate against your station before relying on automations.

## Installation

In HACS, add `andrewt81/hacs-cumulusmx` as a custom **Integration** repository, install, restart Home Assistant, then go to **Settings → Devices & services → Add integration → Cumulus MX**. Enter an address reachable **from Home Assistant**, port (usually 8998), HTTP/HTTPS, and polling interval.

Alternatively copy `custom_components/cumulusmx` into the Home Assistant config directory and restart.

The integration creates temperature, humidity, dew point, pressure, wind speed, gust, bearing, rain today and rain rate sensors. Units are read from Cumulus MX. If your station does not provide a tag, its sensor remains unknown. Today's rainfall is the Cumulus meteorological day, which may roll over at 9/10 a.m. rather than midnight. No credentials, remote access, or Cumulus MX installation are managed here.

## Upstream maintenance

The weekly workflow reads the latest **stable** GitHub release of `cumulusmx/CumulusMX` and opens one `upstream-review` issue per release ID. It highlights API, web tag, JSON, and sensor lines in release notes. A maintainer reviews compatibility manually and publishes an integration GitHub Release if code changes are needed; HACS can then offer that release. Enable Actions and issue creation in repository settings. Workflow checks the latest stable release only and may miss intermediate releases between runs; inspect the official changelog during review. There is no claimed minimum tested Cumulus MX version until a real instance is checked.

## Development

Run `python3 -m compileall custom_components scripts` and `python3 -m json.tool custom_components/cumulusmx/manifest.json`. A live integration test requires a running Home Assistant and Cumulus MX installation.

API: https://www.cumuluswiki.org/a/Cumulus_MX_Local_API
