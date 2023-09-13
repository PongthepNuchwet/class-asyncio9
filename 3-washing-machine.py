import time
import random
import json
import asyncio
import aiomqtt
from enum import Enum
import sys
import time
student_id = "6310301004"


class MachineStatus(Enum):
    pressure = round(random.uniform(2000, 3000), 2)
    temperature = round(random.uniform(25.0, 40.0), 2)


class MachineMaintStatus(Enum):
    filter = random.choice(["clear", "clogged"])
    noise = random.choice(["quiet", "noisy"])


class WashingMachine:
    def __init__(self, serial):
        self.SERIAL = serial
        self.Task = None

        self.MACHINE_STATUS = 'OFF'
        """START | READY | FILLWATER | HEATWATER | WASH | RINSE | SPIN | FAULT"""

        self.FAULT = None
        """TIMEOUT | OUTOFBALANCE | FAULTCLEARED | FAULTCLEARED | None"""

        self.OPERATION = None
        """DOORCLOSE | WATERFULLLEVEL | TEMPERATUREREACHED | COMPLETED"""

        self.OPERATION_value = None
        """" FULL """

    async def Running(self):
        print(
            f"{time.ctime()} - [{self.SERIAL}-{self.MACHINE_STATUS}] START")
        await asyncio.sleep(3600)

    async def Running_Task(self, client):
        self.Task = asyncio.create_task(self.Running())
        wait_coro = asyncio.wait_for(self.Task, timeout=10)
        try:
            await wait_coro
        except asyncio.TimeoutError:
            self.MACHINE_STATUS = 'FAULT'
            self.FAULT = 'TIMEOUT'
            await publish_message(self, client, "hw", "get", "STATUS", self.MACHINE_STATUS)
            await publish_message(self, client, "hw", "get", "FAULT", self.FAULT)
            print(
                f"{time.ctime()} - [{self.SERIAL}-{self.MACHINE_STATUS}] Timeout")

        except asyncio.CancelledError:
            print(
                f"{time.ctime()} - [{self.SERIAL}] Cancelled")

    async def Cancel_Task(self):
        self.Task.cancel()


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


async def CoroWashingMachine(w: WashingMachine, client: aiomqtt.Client, event: asyncio.Event):
    while True:
        # wait_next = round(10*random.random(), 2)
        # print(
        #     f"{time.ctime()} - [{w.SERIAL}-{w.MACHINE_STATUS}] Waiting to start... {wait_next} seconds.")
        # await asyncio.sleep(wait_next)

        if w.MACHINE_STATUS == 'OFF':
            print(
                f"{time.ctime()} - [{w.SERIAL}-{w.MACHINE_STATUS}] Waiting to start...")
            await event.wait()

        if w.MACHINE_STATUS == 'READY':
            await publish_message(w, client, "hw", "get", "STATUS", "READY")
            await publish_message(w, client, 'hw', 'get', 'LID', 'CLOSE')
            w.MACHINE_STATUS = 'FILLWATER'
            await publish_message(w, client, "hw", "get", "STATUS", "FILLWATER")
            await w.Running_Task(client)

        if w.MACHINE_STATUS == 'HEATWATER':
            await publish_message(w, client, "hw", "get", "STATUS", "HEATWATER")
            await w.Running_Task(client)

        if w.MACHINE_STATUS == 'WASH':
            await publish_message(w, client, "hw", "get", "STATUS", "WASH")
            await w.Running_Task(client)

        if w.MACHINE_STATUS == 'RINSE':
            await publish_message(w, client, "hw", "get", "STATUS", "RINSE")
            await w.Running_Task(client)

        if w.MACHINE_STATUS == 'SPIN':
            await publish_message(w, client, "hw", "get", "STATUS", "SPIN")
            await w.Running_Task(client)

        if w.MACHINE_STATUS == 'FAULT':
            print(
                f"{time.ctime()} - [{w.SERIAL}-{w.MACHINE_STATUS}] Waiting to clear fault...")
            await event.wait()

        if event.is_set():
            event.clear()
            # fill water untill full level detected within 10 seconds if not full then timeout

            # heat water until temperature reach 30 celcius within 10 seconds if not reach 30 celcius then timeout

            # wash 10 seconds, if out of balance detected then fault

            # rinse 10 seconds, if motor failure detect then fault

            # spin 10 seconds, if motor failure detect then fault

            # ready state set

            # When washing is in FAULT state, wait until get FAULTCLEARED


async def listen(w: WashingMachine, client: aiomqtt.Client, event: asyncio.Event):
    async with client.messages() as messages:
        await client.subscribe(f"v1cdti/hw/set/{student_id}/model-01/{w.SERIAL}")
        async for message in messages:
            m_decode = json.loads(message.payload)
            if message.topic.matches(f"v1cdti/hw/set/{student_id}/model-01/{w.SERIAL}"):
                # set washing machine status
                print(
                    f"{time.ctime()} - MQTT - [{m_decode['serial']}]:{m_decode['name']} => {m_decode['value']}")

                match m_decode['name']:
                    case "STATUS":
                        w.MACHINE_STATUS = m_decode['value']
                        if m_decode['value'] == 'READY':
                            if not event.is_set():
                                event.set()
                    case "FAULT":
                        if m_decode['value'] == "FAULTCLEARED":
                            w.MACHINE_STATUS = 'OFF'
                            if not event.is_set():
                                event.set()
                        else:
                            w.MACHINE_STATUS = "FAULT"
                            w.FAULT = m_decode['value']
                    case "WATERFULLLEVEL":
                        if w.MACHINE_STATUS == 'FILLWATER' and m_decode['value'] == "FULL":
                            await w.Cancel_Task()
                            w.MACHINE_STATUS = "HEATWATER"
                    case "TEMPERATUREREACHED":
                        if w.MACHINE_STATUS == 'HEATWATER' and m_decode['value'] == "REACHED":
                            await w.Cancel_Task()
                            w.MACHINE_STATUS = "WASH"
                    case 'FUNCTIONCOMPLETED':
                        match m_decode['value']:
                            case "WASH":
                                await w.Cancel_Task()
                                w.MACHINE_STATUS = "RINSE"
                            case "RINSE":
                                await w.Cancel_Task()
                                w.MACHINE_STATUS = "SPIN"
                            case "SPIN":
                                await w.Cancel_Task()
                                w.MACHINE_STATUS = "READY"


async def main():
    w = WashingMachine(serial='SN-001')
    event = asyncio.Event()
    async with aiomqtt.Client("broker.hivemq.com") as client:
        await asyncio.gather(listen(w, client, event), CoroWashingMachine(w, client, event)
                             )

# Change to the "Selector" event loop if platform is Windows
if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())
# Run your async application as usual
asyncio.run(main())
