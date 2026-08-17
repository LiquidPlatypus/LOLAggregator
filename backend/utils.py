import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

REGIONAL_BASE = "https://{region}.api.riotgames.com"
PLATFORM_BASE = "https://{platform}.api.riotgames.com"

def create_url(request, region=None, platform=None, **kwargs):
    if region:
        base = REGIONAL_BASE.format(region=region)
    elif platform:
        base = PLATFORM_BASE.format(platform=platform)
    else:
        raise ValueError("Il faut préciser region= ou platform=")

    return {
        "url": f"{base}{request.format(**kwargs)}",
        "headers": {"X-Riot-Token": API_KEY}
    }