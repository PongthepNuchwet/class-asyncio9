import asyncio
import aiomqtt
import sys 
import os


async def main():
    async with aiomqtt.Client("test.mosquitto.org") as client:
        await client.publish("temperature/outside", payload=28.4)


# Change to the "Selector" event loop if platform is Windows
if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())
# Run your async application as usual
asyncio.run(main())