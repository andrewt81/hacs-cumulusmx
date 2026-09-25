from datetime import timedelta
import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DEFAULT_INTERVAL, DOMAIN, TAGS


def endpoint(data):
    return f"{data['scheme']}://{data['host']}:{data['port']}/api/tags/process.json"


async def fetch(session, data):
    url = endpoint(data)
    # Cumulus requires rc as the first query parameter; tag names are case sensitive.
    try:
        async with session.get(url, params="rc&" + "&".join(TAGS), timeout=aiohttp.ClientTimeout(total=10)) as response:
            response.raise_for_status()
            payload = await response.json(content_type=None)
    except (aiohttp.ClientError, TimeoutError, ValueError) as exc:
        raise UpdateFailed(f"Cannot read Cumulus MX: {exc}") from exc
    if not isinstance(payload, dict) or "temp" not in payload:
        raise UpdateFailed("Unexpected Cumulus MX response")
    return payload


class CumulusCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry, sessions, owns_sessions=False):
        super().__init__(hass, logger=__import__("logging").getLogger(__name__), name=DOMAIN,
                         update_interval=timedelta(seconds=entry.data.get("interval", DEFAULT_INTERVAL)), always_update=False)
        self.entry = entry
        self.sessions = sessions
        self.owns_sessions = owns_sessions

    async def _async_update_data(self):
        failures = []
        for session in self.sessions:
            try:
                return await fetch(session, self.entry.data)
            except UpdateFailed as exc:
                failures.append(str(exc))
        raise UpdateFailed("All configured source addresses failed: " + "; ".join(failures))

    async def close(self):
        if self.owns_sessions:
            for session in self.sessions:
                await session.close()
