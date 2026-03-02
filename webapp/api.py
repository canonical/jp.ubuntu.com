import logging
from canonicalwebteam.http import CachedSession
import yaml
import requests

# this part is temporarily included until
# https://github.com/canonical-webteam/get-feeds
# is updated for flask applications
requests_timeout = 10
expiry_seconds = 300

cached_request = CachedSession(fallback_cache_duration=expiry_seconds)
logger = logging.getLogger(__name__)


def get_releases(url):
    response = requests.get(url)
    response.raise_for_status()
    return yaml.load(response.text, Loader=yaml.FullLoader)


def get(url):
    try:
        response = cached_request.get(url, timeout=requests_timeout)
        response.raise_for_status()
    except Exception as request_error:
        logger.warning(
            "Attempt to get feed failed: {}".format(str(request_error))
        )
        return ""

    return response
