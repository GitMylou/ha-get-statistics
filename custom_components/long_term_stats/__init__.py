async def async_setup(hass, config):
    from .http import LongTermStatsView
    hass.http.register_view(LongTermStatsView)
    return True
