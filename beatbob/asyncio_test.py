import asyncio

async def main():
    print('Hello ...')
    await asyncio.sleep(5)
    print('... World!')

# Python 3.7+
asyncio.run(main())