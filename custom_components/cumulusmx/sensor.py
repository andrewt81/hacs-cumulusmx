from dataclasses import dataclass
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN


@dataclass(frozen=True)
class Reading:
    key: str
    label: str
    unit_tag: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = SensorStateClass.MEASUREMENT


READINGS = (
    Reading("temp", "Outdoor temperature", "tempunitnodeg", SensorDeviceClass.TEMPERATURE),
    Reading("hum", "Humidity", None, SensorDeviceClass.HUMIDITY),
    Reading("dew", "Dew point", "tempunitnodeg", SensorDeviceClass.TEMPERATURE),
    Reading("press", "Pressure", "pressunit", SensorDeviceClass.ATMOSPHERIC_PRESSURE),
    Reading("wspeed", "Wind speed", "windunit", SensorDeviceClass.WIND_SPEED),
    Reading("wgust", "Wind gust", "windunit", SensorDeviceClass.WIND_SPEED),
    Reading("bearing", "Wind direction"),
    Reading("rfall", "Rain today", "rainunit", SensorDeviceClass.PRECIPITATION, None),
    Reading("rrate", "Rain rate", "rainunit", SensorDeviceClass.PRECIPITATION_INTENSITY),
)


def unit(reading, payload):
    if reading.key == "hum":
        return "%"
    if reading.key == "bearing":
        return "°"
    raw = payload.get(reading.unit_tag, "") if reading.unit_tag else ""
    if reading.unit_tag == "tempunitnodeg":
        return {"C": "°C", "F": "°F"}.get(raw)
    if reading.unit_tag == "windunit":
        return {"km/h": "km/h", "mph": "mph", "m/s": "m/s", "kts": "kn"}.get(raw)
    if reading.key == "rrate":
        return {"mm": "mm/h", "inches": "in/h"}.get(raw)
    return {"mb": "hPa", "hPa": "hPa", "in": "inHg", "kPa": "kPa", "mm": "mm", "inches": "in", "in": "in"}.get(raw)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(CumulusSensor(coordinator, entry, item) for item in READINGS)


class CumulusSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, reading):
        super().__init__(coordinator)
        self.reading = reading
        self._attr_unique_id = f"{entry.unique_id}_{reading.key}"
        self._attr_name = reading.label
        self._attr_device_class = reading.device_class
        self._attr_state_class = reading.state_class
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.unique_id)}, "name": entry.title,
                                  "manufacturer": "Cumulus MX", "sw_version": coordinator.data.get("version")}

    @property
    def native_unit_of_measurement(self):
        return unit(self.reading, self.coordinator.data)

    @property
    def native_value(self):
        value = self.coordinator.data.get(self.reading.key)
        if value is None or str(value).strip() in ("", "---", "-999", "-999.0") or "web tag error" in str(value).lower():
            return None
        try:
            return float(str(value).replace(",", "."))
        except ValueError:
            return None
