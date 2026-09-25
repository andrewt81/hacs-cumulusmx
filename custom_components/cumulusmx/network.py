"""Select local source addresses for outbound requests to Cumulus MX."""

from ipaddress import ip_address
import re

import aiohttp


def parse_bind_addresses(raw):
    """Return distinct local IP addresses in priority order."""
    if not raw or not raw.strip():
        return ()
    addresses = []
    for item in re.split(r"[,;\s]+", raw.strip()):
        address = str(ip_address(item))
        if address not in addresses:
            addresses.append(address)
    return tuple(addresses)


def bound_sessions(addresses):
    """Create one dedicated connector per local source address."""
    return [aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(local_addr=(address, 0)), trust_env=False
    ) for address in addresses]
