import time
import random
import json
import asyncio
import aiomqtt
from enum import Enum
import sys
import os

student_id = "6310301004"


class MachineStatus(Enum):
    pressure = round(random.uniform(2000, 3000), 2)
    temperature = round(random.uniform(25.0, 40.0), 2)
    speed = round(random.uniform(25.0, 40.0), 2)
    #
    # add more machine status
    #


class MachineMaintStatus(Enum):
    filter = random.choice(["clear", "clogged"])
    noise = random.choice(["quiet", "noisy"])
    #
    # add more maintenance status
    #

async def Timeout(value):
    await asyncio.sleep(value)

async def FILLWATER(w):
    print(
            f"{time.ctime()} - [{w.SERIAL}] FILLWATER START")
    await asyncio.sleep(100)


class WashingMachine:
    def __init__(self, serial):
        self.MACHINE_STATUS = 'OFF'
        self.STATUS = 'READY'
        # "READY" | "FILLWATER" | "HEATWATER" | "WASH" | "RINSE" | "SPIN"
        self.SERIAL = serial

    async def RUN_FILLWATER(self): 
        self.FILLWATER_TASK = asyncio.create_task(FILLWATER(self))
        self.FILLWATER_TASK_WAIT = asyncio.wait_for(self.FILLWATER_TASK, timeout=10)
        try:
            await self.FILLWATER_TASK_WAIT
        except asyncio.TimeoutError:
            print(f"{time.ctime()} - [{self.SERIAL}] FILLWATER Timeout")
        except asyncio.CancelledError:
            print(f"{time.ctime()} - [{self.SERIAL}] FILLWATER Cancelled")



async def publish_message(w, client, app, action, name, value):
    print(f"{time.ctime()} - [{w.SERIAL}] {name}:{value}")
    await asyncio.sleep(2)
    payload = {
        "action": "get",
        "project": student_id,
        "model": "model-01",
        "serial": w.SERIAL,
        "name": name,
        "value": value
    }
    print(
        f"{time.ctime()} - PUBLISH - [{w.SERIAL}] - {payload['name']} > {payload['value']}")
    await client.publish(f"v1cdti/{app}/{action}/{student_id}/model-01/{w.SERIAL}", payload=json.dumps(payload))




async def CoroWashingMachine(w, client):
    # washing coroutine
    while True:
        wait_next = round(10*random.random(), 2)
        print(
            f"{time.ctime()} - [{w.SERIAL}] Waiting to start... {wait_next} seconds.")
        await asyncio.sleep(wait_next)
        if w.MACHINE_STATUS == 'OFF':
            continue
        else:
            if w.STATUS == 'READY':
                await publish_message(w, client, 'hw', 'get', 'STATUS', 'READY')
                await publish_message(w, client, 'hw', 'get', 'STATUS', 'FILLWATER')
            elif w.STATUS == 'FILLWATER':
                await w.RUN_FILLWATER()
                    




            # await publish_message(w, client, 'hw', 'set', 'LID', 'OPEN')
            # await publish_message(w, client, 'hw', 'set', 'LID', 'CLOSE')

            # status = random.choice(list(MachineStatus))
            # await publish_message(w, client, 'app', 'get', status.name, status.value)
            # await publish_message(w, client, 'app', 'get', "STATUS", "FINISHED")

            # maint = random.choice(list(MachineMaintStatus))
            # await publish_message(w, client, 'app', 'get', maint.name, maint.value)

            # sensor = random.choice(list(MachineStatus))

            # await publish_message(w, client, 'app', 'get', 'SPEED', '100')

            # if maint.name == 'noise' and maint.value == 'noisy':
            #     w.MACHINE_STATUS = 'OFF'
            #     continue

            # w.MACHINE_STATUS = 'OFF'


async def listen(w, client):
    async with client.messages() as messages:
        await client.subscribe(f"v1cdti/hw/set/{student_id}/model-01/{w.SERIAL}")
        async for message in messages:
            m_decode = json.loads(message.payload)
            if message.topic.matches(f"v1cdti/hw/set/{student_id}/model-01/{w.SERIAL}"):
                print(
                    f"{time.ctime()} - MQTT - [{m_decode['serial']}]:{m_decode['name']} => {m_decode['value']}")
                w.MACHINE_STATUS = 'ON'


async def main():
    w1 = WashingMachine(serial='SN-001')
    async with aiomqtt.Client("test.mosquitto.org") as client:
        print(client)
        await asyncio.gather(listen(w1, client), CoroWashingMachine(w1, client))
        # await listen(client)


# Change to the "Selector" event loop if platform is Windows
if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())
# Run your async application as usual
asyncio.run(main())
