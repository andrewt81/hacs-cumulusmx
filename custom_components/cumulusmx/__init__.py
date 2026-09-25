from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN
from .coordinator import CumulusCoordinator
from .network import bound_sessions, parse_bind_addresses

PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    addresses = parse_bind_addresses(entry.data.get("bind_addresses", ""))
    sessions = bound_sessions(addresses) if addresses else [async_get_clientsession(hass)]
    coordinator = CumulusCoordinator(hass, entry, sessions, bool(addresses))
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        await coordinator.close()
        raise
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.close()
        return True
    return False
