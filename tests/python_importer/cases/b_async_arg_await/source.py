async def fetch_value(x):
    return x


async def load_value(x):
    return await fetch_value(x)
