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

    def nextState(self):
        if self.MACHINE_STATUS == 'WASH':
            self.MACHINE_STATUS = 'RINSE'
        elif self.MACHINE_STATUS == 'RINSE':
            self.MACHINE_STATUS = 'SPIN'
        elif self.MACHINE_STATUS == 'SPIN':
            self.MACHINE_STATUS = 'OFF'

    async def Running_Task(self, client: aiomqtt.Client, invert: bool):
        self.Task = asyncio.create_task(self.Running())
        wait_coro = asyncio.wait_for(self.Task, timeout=10)
        try:
            await wait_coro
        except asyncio.TimeoutError:
            print(
                f"{time.ctime()} - [{self.SERIAL}-{self.MACHINE_STATUS}] Timeout")
            if not invert:
                self.MACHINE_STATUS = 'FAULT'
                self.FAULT = 'TIMEOUT'
                await publish_message(self, client, "hw", "get", "STATUS", self.MACHINE_STATUS)
                await publish_message(self, client, "hw", "get", "FAULT", self.FAULT)
            else:
                self.nextState()

        except asyncio.CancelledError:
            print(
                f"{time.ctime()} - [{self.SERIAL}] Cancelled")

    async def Cancel_Task(self):
        self.Task.cancel()


async def publish_message(SERIAL, client, app, action, name, value):
    payload = {
        "action": "get",
        "project": student_id,
        "model": "model-01",
        "serial": SERIAL,
        "name": name,
        "value": value
    }
    print(
        f"{time.ctime()} - PUBLISH - [{SERIAL}] - {payload['name']} > {payload['value']}")
    await client.publish(f"v1cdti/{app}/{action}/{student_id}/model-01/{SERIAL}", payload=json.dumps(payload))


async def listen(client: aiomqtt.Client):
    async with client.messages() as messages:
        await client.subscribe(f"v1cdti/app/get/{student_id}/model-01/+")
        print(
            f"{time.ctime()} - SUB v1cdti/app/get/{student_id}/model-01/+")
        async for message in messages:
            m_decode = json.loads(message.payload)
            if message.topic.matches(f"v1cdti/app/get/{student_id}/model-01/+"):
                # set washing machine status
                print(
                    f"{time.ctime()} - MQTT {m_decode['project']} [{m_decode['serial']}]:{m_decode['name']} => {m_decode['value']}")

                if m_decode['name'] == "STATUS" and m_decode['value'] == 'OFF':
                    await asyncio.sleep(2)
                    await publish_message(m_decode['serial'], client, "hw", "set", "STATUS", "READY")
                elif m_decode['name'] == "STATUS" and m_decode['value'] == 'FILLWATER':
                    await asyncio.sleep(2)
                    await publish_message(m_decode['serial'], client, "hw", "set", "WATERFULLLEVEL", "FULL")
                elif m_decode['name'] == "STATUS" and m_decode['value'] == 'HEATWATER':
                    await asyncio.sleep(2)
                    await publish_message(m_decode['serial'], client, "hw", "set", "TEMPERATUREREACHED", "REACHED")


async def getMachine(client: aiomqtt.Client):
    while True:
        await asyncio.sleep(10)
        payload = {
            "action": "get",
            "project": student_id,
            "model": "model-01",
        }
        print(
            f"{time.ctime()} - PUBLISH - v1cdti/hw/get/{student_id}/model-01/")
        await client.publish(f"v1cdti/hw/get/{student_id}/model-01/", payload=json.dumps(payload))


async def main():
    async with aiomqtt.Client("broker.hivemq.com") as client:

        await asyncio.gather(listen(client), getMachine(client))

# Change to the "Selector" event loop if platform is Windows
if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())
# Run your async application as usual
asyncio.run(main())


# Wed Sep 20 14:32:41 2023 - SUB v1cdti/app/get/6310301004/model-01/+
# Wed Sep 20 14:32:51 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:33:01 2023 - MQTT 6310301004 [SN-001]:STATUS => OFF
# Wed Sep 20 14:33:01 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:33:03 2023 - PUBLISH - [SN-001] - STATUS > READY
# Wed Sep 20 14:33:03 2023 - MQTT 6310301004 [SN-002]:STATUS => OFF
# Wed Sep 20 14:33:05 2023 - PUBLISH - [SN-002] - STATUS > READY
# Wed Sep 20 14:33:05 2023 - MQTT 6310301004 [SN-003]:STATUS => OFF
# Wed Sep 20 14:33:07 2023 - PUBLISH - [SN-003] - STATUS > READY
# Wed Sep 20 14:33:07 2023 - MQTT 6310301004 [SN-004]:STATUS => OFF
# Wed Sep 20 14:33:09 2023 - PUBLISH - [SN-004] - STATUS > READY
# Wed Sep 20 14:33:09 2023 - MQTT 6310301004 [SN-005]:STATUS => OFF
# Wed Sep 20 14:33:11 2023 - PUBLISH - [SN-005] - STATUS > READY
# Wed Sep 20 14:33:11 2023 - MQTT 6310301004 [SN-001]:STATUS => READY
# Wed Sep 20 14:33:11 2023 - MQTT 6310301004 [SN-001]:LID => CLOSE
# Wed Sep 20 14:33:11 2023 - MQTT 6310301004 [SN-001]:STATUS => FILLWATER
# Wed Sep 20 14:33:11 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:33:13 2023 - PUBLISH - [SN-001] - WATERFULLLEVEL > FULL
# Wed Sep 20 14:33:13 2023 - MQTT 6310301004 [SN-002]:STATUS => READY
# Wed Sep 20 14:33:13 2023 - MQTT 6310301004 [SN-002]:LID => CLOSE
# Wed Sep 20 14:33:13 2023 - MQTT 6310301004 [SN-002]:STATUS => FILLWATER
# Wed Sep 20 14:33:15 2023 - PUBLISH - [SN-002] - WATERFULLLEVEL > FULL
# Wed Sep 20 14:33:15 2023 - MQTT 6310301004 [SN-003]:STATUS => READY
# Wed Sep 20 14:33:15 2023 - MQTT 6310301004 [SN-003]:LID => CLOSE
# Wed Sep 20 14:33:15 2023 - MQTT 6310301004 [SN-003]:STATUS => FILLWATER
# Wed Sep 20 14:33:17 2023 - PUBLISH - [SN-003] - WATERFULLLEVEL > FULL
# Wed Sep 20 14:33:17 2023 - MQTT 6310301004 [SN-004]:STATUS => READY
# Wed Sep 20 14:33:17 2023 - MQTT 6310301004 [SN-004]:LID => CLOSE
# Wed Sep 20 14:33:17 2023 - MQTT 6310301004 [SN-004]:STATUS => FILLWATER
# Wed Sep 20 14:33:19 2023 - PUBLISH - [SN-004] - WATERFULLLEVEL > FULL
# Wed Sep 20 14:33:19 2023 - MQTT 6310301004 [SN-005]:STATUS => READY
# Wed Sep 20 14:33:19 2023 - MQTT 6310301004 [SN-005]:LID => CLOSE
# Wed Sep 20 14:33:19 2023 - MQTT 6310301004 [SN-005]:STATUS => FILLWATER
# Wed Sep 20 14:33:21 2023 - PUBLISH - [SN-005] - WATERFULLLEVEL > FULL
# Wed Sep 20 14:33:21 2023 - MQTT 6310301004 [SN-001]:STATUS => HEATWATER
# Wed Sep 20 14:33:21 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:33:23 2023 - PUBLISH - [SN-001] - TEMPERATUREREACHED > REACHED
# Wed Sep 20 14:33:23 2023 - MQTT 6310301004 [SN-002]:STATUS => HEATWATER
# Wed Sep 20 14:33:25 2023 - PUBLISH - [SN-002] - TEMPERATUREREACHED > REACHED
# Wed Sep 20 14:33:25 2023 - MQTT 6310301004 [SN-003]:STATUS => HEATWATER
# Wed Sep 20 14:33:27 2023 - PUBLISH - [SN-003] - TEMPERATUREREACHED > REACHED
# Wed Sep 20 14:33:27 2023 - MQTT 6310301004 [SN-004]:STATUS => HEATWATER
# Wed Sep 20 14:33:29 2023 - PUBLISH - [SN-004] - TEMPERATUREREACHED > REACHED
# Wed Sep 20 14:33:29 2023 - MQTT 6310301004 [SN-005]:STATUS => HEATWATER
# Wed Sep 20 14:33:31 2023 - PUBLISH - [SN-005] - TEMPERATUREREACHED > REACHED
# Wed Sep 20 14:33:31 2023 - MQTT 6310301004 [SN-001]:STATUS => WASH
# Wed Sep 20 14:33:31 2023 - MQTT 6310301004 [SN-002]:STATUS => WASH
# Wed Sep 20 14:33:31 2023 - MQTT 6310301004 [SN-003]:STATUS => WASH
# Wed Sep 20 14:33:31 2023 - MQTT 6310301004 [SN-004]:STATUS => WASH
# Wed Sep 20 14:33:31 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:33:31 2023 - MQTT 6310301004 [SN-005]:STATUS => WASH
# Wed Sep 20 14:33:41 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:33:43 2023 - MQTT 6310301004 [SN-001]:STATUS => RINSE
# Wed Sep 20 14:33:45 2023 - MQTT 6310301004 [SN-002]:STATUS => RINSE
# Wed Sep 20 14:33:47 2023 - MQTT 6310301004 [SN-003]:STATUS => RINSE
# Wed Sep 20 14:33:49 2023 - MQTT 6310301004 [SN-004]:STATUS => RINSE
# Wed Sep 20 14:33:51 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:33:52 2023 - MQTT 6310301004 [SN-005]:STATUS => RINSE
# Wed Sep 20 14:34:01 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:34:03 2023 - MQTT 6310301004 [SN-001]:STATUS => SPIN
# Wed Sep 20 14:34:05 2023 - MQTT 6310301004 [SN-002]:STATUS => SPIN
# Wed Sep 20 14:34:07 2023 - MQTT 6310301004 [SN-003]:STATUS => SPIN
# Wed Sep 20 14:34:09 2023 - MQTT 6310301004 [SN-004]:STATUS => SPIN
# Wed Sep 20 14:34:11 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:34:11 2023 - MQTT 6310301004 [SN-005]:STATUS => SPIN
# Wed Sep 20 14:34:21 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:34:23 2023 - MQTT 6310301004 [SN-001]:STATUS => OFF
# Wed Sep 20 14:34:25 2023 - PUBLISH - [SN-001] - STATUS > READY
# Wed Sep 20 14:34:25 2023 - MQTT 6310301004 [SN-002]:STATUS => OFF
# Wed Sep 20 14:34:27 2023 - PUBLISH - [SN-002] - STATUS > READY
# Wed Sep 20 14:34:27 2023 - MQTT 6310301004 [SN-001]:STATUS => READY
# Wed Sep 20 14:34:27 2023 - MQTT 6310301004 [SN-001]:LID => CLOSE
# Wed Sep 20 14:34:27 2023 - MQTT 6310301004 [SN-001]:STATUS => FILLWATER
# Wed Sep 20 14:34:29 2023 - PUBLISH - [SN-001] - WATERFULLLEVEL > FULL
# Wed Sep 20 14:34:29 2023 - MQTT 6310301004 [SN-003]:STATUS => OFF
# Wed Sep 20 14:34:31 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:34:31 2023 - PUBLISH - [SN-003] - STATUS > READY
# Wed Sep 20 14:34:31 2023 - MQTT 6310301004 [SN-002]:STATUS => READY
# Wed Sep 20 14:34:31 2023 - MQTT 6310301004 [SN-002]:LID => CLOSE
# Wed Sep 20 14:34:31 2023 - MQTT 6310301004 [SN-002]:STATUS => FILLWATER
# Wed Sep 20 14:34:33 2023 - PUBLISH - [SN-002] - WATERFULLLEVEL > FULL
# Wed Sep 20 14:34:33 2023 - MQTT 6310301004 [SN-004]:STATUS => OFF
# Wed Sep 20 14:34:35 2023 - PUBLISH - [SN-004] - STATUS > READY
# Wed Sep 20 14:34:35 2023 - MQTT 6310301004 [SN-001]:STATUS => HEATWATER
# Wed Sep 20 14:34:38 2023 - PUBLISH - [SN-001] - TEMPERATUREREACHED > REACHED
# Wed Sep 20 14:34:38 2023 - MQTT 6310301004 [SN-005]:STATUS => OFF
# Wed Sep 20 14:34:40 2023 - PUBLISH - [SN-005] - STATUS > READY
# Wed Sep 20 14:34:40 2023 - MQTT 6310301004 [SN-003]:STATUS => READY
# Wed Sep 20 14:34:40 2023 - MQTT 6310301004 [SN-003]:LID => CLOSE
# Wed Sep 20 14:34:40 2023 - MQTT 6310301004 [SN-003]:STATUS => FILLWATER
# Wed Sep 20 14:34:41 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:34:42 2023 - PUBLISH - [SN-003] - WATERFULLLEVEL > FULL
# Wed Sep 20 14:34:42 2023 - MQTT 6310301004 [SN-002]:STATUS => HEATWATER
# Wed Sep 20 14:34:44 2023 - PUBLISH - [SN-002] - TEMPERATUREREACHED > REACHED
# Wed Sep 20 14:34:44 2023 - MQTT 6310301004 [SN-004]:STATUS => READY
# Wed Sep 20 14:34:44 2023 - MQTT 6310301004 [SN-004]:LID => CLOSE
# Wed Sep 20 14:34:44 2023 - MQTT 6310301004 [SN-004]:STATUS => FILLWATER
# Wed Sep 20 14:34:46 2023 - PUBLISH - [SN-004] - WATERFULLLEVEL > FULL
# Wed Sep 20 14:34:46 2023 - MQTT 6310301004 [SN-001]:STATUS => WASH
# Wed Sep 20 14:34:46 2023 - MQTT 6310301004 [SN-005]:STATUS => READY
# Wed Sep 20 14:34:46 2023 - MQTT 6310301004 [SN-005]:LID => CLOSE
# Wed Sep 20 14:34:46 2023 - MQTT 6310301004 [SN-005]:STATUS => FILLWATER
# Wed Sep 20 14:34:48 2023 - PUBLISH - [SN-005] - WATERFULLLEVEL > FULL
# Wed Sep 20 14:34:48 2023 - MQTT 6310301004 [SN-003]:STATUS => HEATWATER
# Wed Sep 20 14:34:50 2023 - PUBLISH - [SN-003] - TEMPERATUREREACHED > REACHED
# Wed Sep 20 14:34:50 2023 - MQTT 6310301004 [SN-002]:STATUS => WASH
# Wed Sep 20 14:34:50 2023 - MQTT 6310301004 [SN-004]:STATUS => HEATWATER
# Wed Sep 20 14:34:51 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:34:52 2023 - PUBLISH - [SN-004] - TEMPERATUREREACHED > REACHED
# Wed Sep 20 14:34:52 2023 - MQTT 6310301004 [SN-005]:STATUS => HEATWATER
# Wed Sep 20 14:34:54 2023 - PUBLISH - [SN-005] - TEMPERATUREREACHED > REACHED
# Wed Sep 20 14:34:54 2023 - MQTT 6310301004 [SN-003]:STATUS => WASH
# Wed Sep 20 14:34:54 2023 - MQTT 6310301004 [SN-004]:STATUS => WASH
# Wed Sep 20 14:34:54 2023 - MQTT 6310301004 [SN-005]:STATUS => WASH
# Wed Sep 20 14:34:58 2023 - MQTT 6310301004 [SN-001]:STATUS => RINSE
# Wed Sep 20 14:35:01 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:35:04 2023 - MQTT 6310301004 [SN-002]:STATUS => RINSE
# Wed Sep 20 14:35:10 2023 - MQTT 6310301004 [SN-003]:STATUS => RINSE
# Wed Sep 20 14:35:11 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:35:12 2023 - MQTT 6310301004 [SN-004]:STATUS => RINSE
# Wed Sep 20 14:35:14 2023 - MQTT 6310301004 [SN-005]:STATUS => RINSE
# Wed Sep 20 14:35:18 2023 - MQTT 6310301004 [SN-001]:STATUS => SPIN
# Wed Sep 20 14:35:21 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:35:24 2023 - MQTT 6310301004 [SN-002]:STATUS => SPIN
# Wed Sep 20 14:35:30 2023 - MQTT 6310301004 [SN-003]:STATUS => SPIN
# Wed Sep 20 14:35:31 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:35:32 2023 - MQTT 6310301004 [SN-004]:STATUS => SPIN
# Wed Sep 20 14:35:34 2023 - MQTT 6310301004 [SN-005]:STATUS => SPIN
# Wed Sep 20 14:35:38 2023 - MQTT 6310301004 [SN-001]:STATUS => OFF
# Wed Sep 20 14:35:40 2023 - PUBLISH - [SN-001] - STATUS > READY
# Wed Sep 20 14:35:40 2023 - MQTT 6310301004 [SN-001]:STATUS => READY
# Wed Sep 20 14:35:41 2023 - MQTT 6310301004 [SN-001]:LID => CLOSE
# Wed Sep 20 14:35:41 2023 - MQTT 6310301004 [SN-001]:STATUS => FILLWATER
# Wed Sep 20 14:35:41 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:35:43 2023 - PUBLISH - [SN-001] - WATERFULLLEVEL > FULL
# Wed Sep 20 14:35:43 2023 - MQTT 6310301004 [SN-001]:STATUS => HEATWATER
# Wed Sep 20 14:35:45 2023 - PUBLISH - [SN-001] - TEMPERATUREREACHED > REACHED
# Wed Sep 20 14:35:45 2023 - MQTT 6310301004 [SN-002]:STATUS => OFF
# Wed Sep 20 14:35:47 2023 - PUBLISH - [SN-002] - STATUS > READY
# Wed Sep 20 14:35:47 2023 - MQTT 6310301004 [SN-001]:STATUS => WASH
# Wed Sep 20 14:35:47 2023 - MQTT 6310301004 [SN-002]:STATUS => READY
# Wed Sep 20 14:35:48 2023 - MQTT 6310301004 [SN-002]:LID => CLOSE
# Wed Sep 20 14:35:48 2023 - MQTT 6310301004 [SN-002]:STATUS => FILLWATER
# Wed Sep 20 14:35:50 2023 - PUBLISH - [SN-002] - WATERFULLLEVEL > FULL
# Wed Sep 20 14:35:50 2023 - MQTT 6310301004 [SN-003]:STATUS => OFF
# Wed Sep 20 14:35:51 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:35:52 2023 - PUBLISH - [SN-003] - STATUS > READY
# Wed Sep 20 14:35:52 2023 - MQTT 6310301004 [SN-002]:STATUS => HEATWATER
# Wed Sep 20 14:35:54 2023 - PUBLISH - [SN-002] - TEMPERATUREREACHED > REACHED
# Wed Sep 20 14:35:54 2023 - MQTT 6310301004 [SN-004]:STATUS => OFF
# Wed Sep 20 14:35:56 2023 - PUBLISH - [SN-004] - STATUS > READY
# Wed Sep 20 14:35:56 2023 - MQTT 6310301004 [SN-003]:STATUS => READY
# Wed Sep 20 14:35:56 2023 - MQTT 6310301004 [SN-003]:LID => CLOSE
# Wed Sep 20 14:35:56 2023 - MQTT 6310301004 [SN-003]:STATUS => FILLWATER
# Wed Sep 20 14:35:58 2023 - PUBLISH - [SN-003] - WATERFULLLEVEL > FULL
# Wed Sep 20 14:35:58 2023 - MQTT 6310301004 [SN-005]:STATUS => OFF
# Wed Sep 20 14:36:00 2023 - PUBLISH - [SN-005] - STATUS > READY
# Wed Sep 20 14:36:00 2023 - MQTT 6310301004 [SN-002]:STATUS => WASH
# Wed Sep 20 14:36:00 2023 - MQTT 6310301004 [SN-004]:STATUS => READY
# Wed Sep 20 14:36:00 2023 - MQTT 6310301004 [SN-004]:LID => CLOSE
# Wed Sep 20 14:36:00 2023 - MQTT 6310301004 [SN-004]:STATUS => FILLWATER
# Wed Sep 20 14:36:01 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:36:02 2023 - PUBLISH - [SN-004] - WATERFULLLEVEL > FULL
# Wed Sep 20 14:36:02 2023 - MQTT 6310301004 [SN-003]:STATUS => HEATWATER
# Wed Sep 20 14:36:04 2023 - PUBLISH - [SN-003] - TEMPERATUREREACHED > REACHED
# Wed Sep 20 14:36:04 2023 - MQTT 6310301004 [SN-005]:STATUS => READY
# Wed Sep 20 14:36:04 2023 - MQTT 6310301004 [SN-005]:LID => CLOSE
# Wed Sep 20 14:36:04 2023 - MQTT 6310301004 [SN-005]:STATUS => FILLWATER
# Wed Sep 20 14:36:06 2023 - PUBLISH - [SN-005] - WATERFULLLEVEL > FULL
# Wed Sep 20 14:36:06 2023 - MQTT 6310301004 [SN-004]:STATUS => HEATWATER
# Wed Sep 20 14:36:08 2023 - PUBLISH - [SN-004] - TEMPERATUREREACHED > REACHED
# Wed Sep 20 14:36:08 2023 - MQTT 6310301004 [SN-003]:STATUS => WASH
# Wed Sep 20 14:36:08 2023 - MQTT 6310301004 [SN-001]:STATUS => RINSE
# Wed Sep 20 14:36:08 2023 - MQTT 6310301004 [SN-005]:STATUS => HEATWATER
# Wed Sep 20 14:36:10 2023 - PUBLISH - [SN-005] - TEMPERATUREREACHED > REACHED
# Wed Sep 20 14:36:10 2023 - MQTT 6310301004 [SN-004]:STATUS => WASH
# Wed Sep 20 14:36:10 2023 - MQTT 6310301004 [SN-005]:STATUS => WASH
# Wed Sep 20 14:36:11 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:36:14 2023 - MQTT 6310301004 [SN-002]:STATUS => RINSE
# Wed Sep 20 14:36:21 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:36:24 2023 - MQTT 6310301004 [SN-003]:STATUS => RINSE
# Wed Sep 20 14:36:25 2023 - MQTT 6310301004 [SN-001]:STATUS => SPIN
# Wed Sep 20 14:36:28 2023 - MQTT 6310301004 [SN-004]:STATUS => RINSE
# Wed Sep 20 14:36:30 2023 - MQTT 6310301004 [SN-005]:STATUS => RINSE
# Wed Sep 20 14:36:31 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:36:34 2023 - MQTT 6310301004 [SN-002]:STATUS => SPIN
# Wed Sep 20 14:36:41 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:36:44 2023 - MQTT 6310301004 [SN-003]:STATUS => SPIN
# Wed Sep 20 14:36:45 2023 - MQTT 6310301004 [SN-001]:STATUS => OFF
# Wed Sep 20 14:36:47 2023 - PUBLISH - [SN-001] - STATUS > READY
# Wed Sep 20 14:36:48 2023 - MQTT 6310301004 [SN-001]:STATUS => READY
# Wed Sep 20 14:36:48 2023 - MQTT 6310301004 [SN-001]:LID => CLOSE
# Wed Sep 20 14:36:48 2023 - MQTT 6310301004 [SN-001]:STATUS => FILLWATER
# Wed Sep 20 14:36:50 2023 - PUBLISH - [SN-001] - WATERFULLLEVEL > FULL
# Wed Sep 20 14:36:50 2023 - MQTT 6310301004 [SN-004]:STATUS => SPIN
# Wed Sep 20 14:36:50 2023 - MQTT 6310301004 [SN-001]:STATUS => HEATWATER
# Wed Sep 20 14:36:51 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:36:52 2023 - PUBLISH - [SN-001] - TEMPERATUREREACHED > REACHED
# Wed Sep 20 14:36:52 2023 - MQTT 6310301004 [SN-005]:STATUS => SPIN
# Wed Sep 20 14:36:53 2023 - MQTT 6310301004 [SN-001]:STATUS => WASH
# Wed Sep 20 14:36:54 2023 - MQTT 6310301004 [SN-002]:STATUS => OFF
# Wed Sep 20 14:36:56 2023 - PUBLISH - [SN-002] - STATUS > READY
# Wed Sep 20 14:36:57 2023 - MQTT 6310301004 [SN-002]:STATUS => READY
# Wed Sep 20 14:36:57 2023 - MQTT 6310301004 [SN-002]:LID => CLOSE
# Wed Sep 20 14:36:57 2023 - MQTT 6310301004 [SN-002]:STATUS => FILLWATER
# Wed Sep 20 14:36:59 2023 - PUBLISH - [SN-002] - WATERFULLLEVEL > FULL
# Wed Sep 20 14:37:00 2023 - MQTT 6310301004 [SN-002]:STATUS => HEATWATER
# Wed Sep 20 14:37:01 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:37:02 2023 - PUBLISH - [SN-002] - TEMPERATUREREACHED > REACHED
# Wed Sep 20 14:37:02 2023 - MQTT 6310301004 [SN-002]:STATUS => WASH
# Wed Sep 20 14:37:04 2023 - MQTT 6310301004 [SN-003]:STATUS => OFF
# Wed Sep 20 14:37:06 2023 - PUBLISH - [SN-003] - STATUS > READY
# Wed Sep 20 14:37:07 2023 - MQTT 6310301004 [SN-003]:STATUS => READY
# Wed Sep 20 14:37:07 2023 - MQTT 6310301004 [SN-003]:LID => CLOSE
# Wed Sep 20 14:37:07 2023 - MQTT 6310301004 [SN-003]:STATUS => FILLWATER
# Wed Sep 20 14:37:09 2023 - PUBLISH - [SN-003] - WATERFULLLEVEL > FULL
# Wed Sep 20 14:37:09 2023 - MQTT 6310301004 [SN-004]:STATUS => OFF
# Wed Sep 20 14:37:11 2023 - PUBLISH - [SN-004] - STATUS > READY
# Wed Sep 20 14:37:11 2023 - MQTT 6310301004 [SN-003]:STATUS => HEATWATER
# Wed Sep 20 14:37:11 2023 - PUBLISH - v1cdti/hw/get/6310301004/model-01/
# Wed Sep 20 14:37:13 2023 - PUBLISH - [SN-003] - TEMPERATUREREACHED > REACHED
# Wed Sep 20 14:37:13 2023 - MQTT 6310301004 [SN-005]:STATUS => OFF