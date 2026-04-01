async def fetch_value():
    return 1


async def load_once():
    return await fetch_value()
