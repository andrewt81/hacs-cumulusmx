import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import UpdateFailed
from .const import DEFAULT_INTERVAL, DEFAULT_PORT, DOMAIN
from .coordinator import fetch


class CumulusFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            user_input["host"] = user_input["host"].strip()
            if not user_input["host"] or any(c in user_input["host"] for c in "/?#@ "):
                errors["host"] = "invalid_host"
            else:
                await self.async_set_unique_id(f"{user_input['scheme']}://{user_input['host'].lower()}:{user_input['port']}")
                self._abort_if_unique_id_configured()
                try:
                    await fetch(async_get_clientsession(self.hass), user_input)
                except UpdateFailed:
                    errors["base"] = "cannot_connect"
                else:
                    return self.async_create_entry(title=f"Cumulus MX ({user_input['host']})", data=user_input)
        return self.async_show_form(step_id="user", data_schema=vol.Schema({
            vol.Required("host", default=(user_input or {}).get("host", "")): str,
            vol.Required("port", default=(user_input or {}).get("port", DEFAULT_PORT)): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
            vol.Required("scheme", default=(user_input or {}).get("scheme", "http")): vol.In(["http", "https"]),
            vol.Required("interval", default=(user_input or {}).get("interval", DEFAULT_INTERVAL)): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
        }), errors=errors)
