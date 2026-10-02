import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")


@mcp.tool()
def get_weather(location: str) -> str:
    """Get the current weather for a location (city or place name)."""
    geo = httpx.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": location, "count": 1, "language": "en", "format": "json"},
        timeout=10,
    ).json()
    results = geo.get("results")
    if not results:
        return f"Could not find location: {location}"
    place = results[0]
    lat, lon = place["latitude"], place["longitude"]

    forecast = httpx.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        },
        timeout=10,
    ).json()

    current = forecast.get("current", {})
    return (
        f"Weather in {place.get('name')}, {place.get('country')}:\n"
        f"- Temperature: {current.get('temperature_2m')} °C\n"
        f"- Humidity: {current.get('relative_humidity_2m')} %\n"
        f"- Wind speed: {current.get('wind_speed_10m')} km/h"
    )


if __name__ == "__main__":
    mcp.run()
