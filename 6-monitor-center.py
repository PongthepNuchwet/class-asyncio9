import time
import random
import json
import asyncio
import aiomqtt
from enum import Enum
import sys
import time
student_id = "6310301004"


async def listen(client: aiomqtt.Client):
    async with client.messages() as messages:
        await client.subscribe(f"v1cdti/app/monitor/{student_id}/model-01/+")
        print(
            f"{time.ctime()} - SUB v1cdti/app/monitor/{student_id}/model-01/+")
        async for message in messages:
            m_decode = json.loads(message.payload)
            if message.topic.matches(f"v1cdti/app/monitor/{student_id}/model-01/+"):
                # set washing machine status
                print(
                    f"{time.ctime()} - MQTT - [{m_decode['serial']}]:{m_decode['name']} => {m_decode['value']}")


async def main():

    async with aiomqtt.Client("broker.hivemq.com") as client:
        await asyncio.gather(listen(client))

# Change to the "Selector" event loop if platform is Windows
if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())
# Run your async application as usual
asyncio.run(main())


# Wed Sep 20 14:32:44 2023 - SUB v1cdti/app/monitor/6310301004/model-01/+
# Wed Sep 20 14:33:02 2023 - MQTT - [SN-001]:STATUS => OFF
# Wed Sep 20 14:33:02 2023 - MQTT - [SN-002]:STATUS => OFF
# Wed Sep 20 14:33:02 2023 - MQTT - [SN-003]:STATUS => OFF
# Wed Sep 20 14:33:02 2023 - MQTT - [SN-004]:STATUS => OFF
# Wed Sep 20 14:33:02 2023 - MQTT - [SN-005]:STATUS => OFF
# Wed Sep 20 14:33:12 2023 - MQTT - [SN-001]:STATUS => FILLWATER
# Wed Sep 20 14:33:12 2023 - MQTT - [SN-002]:STATUS => FILLWATER
# Wed Sep 20 14:33:12 2023 - MQTT - [SN-003]:STATUS => FILLWATER
# Wed Sep 20 14:33:12 2023 - MQTT - [SN-004]:STATUS => FILLWATER
# Wed Sep 20 14:33:12 2023 - MQTT - [SN-005]:STATUS => FILLWATER
# Wed Sep 20 14:33:22 2023 - MQTT - [SN-001]:STATUS => HEATWATER
# Wed Sep 20 14:33:22 2023 - MQTT - [SN-002]:STATUS => HEATWATER
# Wed Sep 20 14:33:22 2023 - MQTT - [SN-003]:STATUS => HEATWATER
# Wed Sep 20 14:33:22 2023 - MQTT - [SN-004]:STATUS => HEATWATER
# Wed Sep 20 14:33:22 2023 - MQTT - [SN-005]:STATUS => HEATWATER
# Wed Sep 20 14:33:32 2023 - MQTT - [SN-001]:STATUS => WASH
# Wed Sep 20 14:33:32 2023 - MQTT - [SN-002]:STATUS => WASH
# Wed Sep 20 14:33:32 2023 - MQTT - [SN-003]:STATUS => WASH
# Wed Sep 20 14:33:32 2023 - MQTT - [SN-004]:STATUS => WASH
# Wed Sep 20 14:33:32 2023 - MQTT - [SN-005]:STATUS => WASH
# Wed Sep 20 14:33:42 2023 - MQTT - [SN-001]:STATUS => WASH
# Wed Sep 20 14:33:42 2023 - MQTT - [SN-002]:STATUS => WASH
# Wed Sep 20 14:33:42 2023 - MQTT - [SN-003]:STATUS => WASH
# Wed Sep 20 14:33:42 2023 - MQTT - [SN-004]:STATUS => WASH
# Wed Sep 20 14:33:42 2023 - MQTT - [SN-005]:STATUS => WASH
# Wed Sep 20 14:33:52 2023 - MQTT - [SN-001]:STATUS => RINSE
# Wed Sep 20 14:33:52 2023 - MQTT - [SN-002]:STATUS => RINSE
# Wed Sep 20 14:33:52 2023 - MQTT - [SN-003]:STATUS => RINSE
# Wed Sep 20 14:33:52 2023 - MQTT - [SN-004]:STATUS => RINSE
# Wed Sep 20 14:33:52 2023 - MQTT - [SN-005]:STATUS => RINSE
# Wed Sep 20 14:34:02 2023 - MQTT - [SN-001]:STATUS => RINSE
# Wed Sep 20 14:34:02 2023 - MQTT - [SN-002]:STATUS => RINSE
# Wed Sep 20 14:34:02 2023 - MQTT - [SN-003]:STATUS => RINSE
# Wed Sep 20 14:34:02 2023 - MQTT - [SN-004]:STATUS => RINSE
# Wed Sep 20 14:34:02 2023 - MQTT - [SN-005]:STATUS => RINSE
# Wed Sep 20 14:34:12 2023 - MQTT - [SN-001]:STATUS => SPIN
# Wed Sep 20 14:34:12 2023 - MQTT - [SN-002]:STATUS => SPIN
# Wed Sep 20 14:34:12 2023 - MQTT - [SN-003]:STATUS => SPIN
# Wed Sep 20 14:34:12 2023 - MQTT - [SN-004]:STATUS => SPIN
# Wed Sep 20 14:34:12 2023 - MQTT - [SN-005]:STATUS => SPIN
# Wed Sep 20 14:34:22 2023 - MQTT - [SN-001]:STATUS => SPIN
# Wed Sep 20 14:34:22 2023 - MQTT - [SN-002]:STATUS => SPIN
# Wed Sep 20 14:34:22 2023 - MQTT - [SN-003]:STATUS => SPIN
# Wed Sep 20 14:34:22 2023 - MQTT - [SN-004]:STATUS => SPIN
# Wed Sep 20 14:34:22 2023 - MQTT - [SN-005]:STATUS => SPIN
# Wed Sep 20 14:34:32 2023 - MQTT - [SN-001]:STATUS => HEATWATER
# Wed Sep 20 14:34:32 2023 - MQTT - [SN-002]:STATUS => FILLWATER
# Wed Sep 20 14:34:32 2023 - MQTT - [SN-003]:STATUS => OFF
# Wed Sep 20 14:34:32 2023 - MQTT - [SN-004]:STATUS => OFF
# Wed Sep 20 14:34:32 2023 - MQTT - [SN-005]:STATUS => OFF
# Wed Sep 20 14:34:42 2023 - MQTT - [SN-001]:STATUS => WASH
# Wed Sep 20 14:34:42 2023 - MQTT - [SN-002]:STATUS => HEATWATER
# Wed Sep 20 14:34:42 2023 - MQTT - [SN-003]:STATUS => FILLWATER
# Wed Sep 20 14:34:42 2023 - MQTT - [SN-004]:STATUS => FILLWATER
# Wed Sep 20 14:34:42 2023 - MQTT - [SN-005]:STATUS => FILLWATER
# Wed Sep 20 14:34:52 2023 - MQTT - [SN-001]:STATUS => WASH
# Wed Sep 20 14:34:52 2023 - MQTT - [SN-002]:STATUS => WASH
# Wed Sep 20 14:34:52 2023 - MQTT - [SN-003]:STATUS => WASH
# Wed Sep 20 14:34:52 2023 - MQTT - [SN-004]:STATUS => HEATWATER
# Wed Sep 20 14:34:52 2023 - MQTT - [SN-005]:STATUS => HEATWATER
# Wed Sep 20 14:35:02 2023 - MQTT - [SN-001]:STATUS => RINSE
# Wed Sep 20 14:35:02 2023 - MQTT - [SN-002]:STATUS => WASH
# Wed Sep 20 14:35:02 2023 - MQTT - [SN-003]:STATUS => WASH
# Wed Sep 20 14:35:02 2023 - MQTT - [SN-004]:STATUS => WASH
# Wed Sep 20 14:35:02 2023 - MQTT - [SN-005]:STATUS => WASH
# Wed Sep 20 14:35:12 2023 - MQTT - [SN-001]:STATUS => RINSE
# Wed Sep 20 14:35:12 2023 - MQTT - [SN-002]:STATUS => RINSE
# Wed Sep 20 14:35:12 2023 - MQTT - [SN-003]:STATUS => RINSE
# Wed Sep 20 14:35:12 2023 - MQTT - [SN-004]:STATUS => WASH
# Wed Sep 20 14:35:12 2023 - MQTT - [SN-005]:STATUS => WASH
# Wed Sep 20 14:35:22 2023 - MQTT - [SN-001]:STATUS => SPIN
# Wed Sep 20 14:35:22 2023 - MQTT - [SN-002]:STATUS => RINSE
# Wed Sep 20 14:35:22 2023 - MQTT - [SN-003]:STATUS => RINSE
# Wed Sep 20 14:35:22 2023 - MQTT - [SN-004]:STATUS => RINSE
# Wed Sep 20 14:35:22 2023 - MQTT - [SN-005]:STATUS => RINSE
# Wed Sep 20 14:35:32 2023 - MQTT - [SN-001]:STATUS => SPIN
# Wed Sep 20 14:35:32 2023 - MQTT - [SN-002]:STATUS => SPIN
# Wed Sep 20 14:35:32 2023 - MQTT - [SN-003]:STATUS => SPIN
# Wed Sep 20 14:35:32 2023 - MQTT - [SN-004]:STATUS => RINSE
# Wed Sep 20 14:35:32 2023 - MQTT - [SN-005]:STATUS => RINSE
# Wed Sep 20 14:35:42 2023 - MQTT - [SN-001]:STATUS => FILLWATER
# Wed Sep 20 14:35:42 2023 - MQTT - [SN-002]:STATUS => SPIN
# Wed Sep 20 14:35:42 2023 - MQTT - [SN-003]:STATUS => SPIN
# Wed Sep 20 14:35:42 2023 - MQTT - [SN-004]:STATUS => SPIN
# Wed Sep 20 14:35:42 2023 - MQTT - [SN-005]:STATUS => SPIN
# Wed Sep 20 14:35:52 2023 - MQTT - [SN-001]:STATUS => WASH
# Wed Sep 20 14:35:52 2023 - MQTT - [SN-002]:STATUS => HEATWATER
# Wed Sep 20 14:35:52 2023 - MQTT - [SN-003]:STATUS => OFF
# Wed Sep 20 14:35:52 2023 - MQTT - [SN-004]:STATUS => SPIN
# Wed Sep 20 14:35:52 2023 - MQTT - [SN-005]:STATUS => SPIN
# Wed Sep 20 14:36:02 2023 - MQTT - [SN-001]:STATUS => WASH
# Wed Sep 20 14:36:02 2023 - MQTT - [SN-002]:STATUS => WASH
# Wed Sep 20 14:36:02 2023 - MQTT - [SN-003]:STATUS => HEATWATER
# Wed Sep 20 14:36:02 2023 - MQTT - [SN-004]:STATUS => FILLWATER
# Wed Sep 20 14:36:02 2023 - MQTT - [SN-005]:STATUS => FILLWATER
# Wed Sep 20 14:36:12 2023 - MQTT - [SN-001]:STATUS => RINSE
# Wed Sep 20 14:36:12 2023 - MQTT - [SN-002]:STATUS => WASH
# Wed Sep 20 14:36:12 2023 - MQTT - [SN-003]:STATUS => WASH
# Wed Sep 20 14:36:12 2023 - MQTT - [SN-004]:STATUS => WASH
# Wed Sep 20 14:36:12 2023 - MQTT - [SN-005]:STATUS => WASH
# Wed Sep 20 14:36:22 2023 - MQTT - [SN-001]:STATUS => RINSE
# Wed Sep 20 14:36:22 2023 - MQTT - [SN-002]:STATUS => RINSE
# Wed Sep 20 14:36:22 2023 - MQTT - [SN-003]:STATUS => WASH
# Wed Sep 20 14:36:22 2023 - MQTT - [SN-004]:STATUS => WASH
# Wed Sep 20 14:36:22 2023 - MQTT - [SN-005]:STATUS => WASH
# Wed Sep 20 14:36:32 2023 - MQTT - [SN-001]:STATUS => SPIN
# Wed Sep 20 14:36:32 2023 - MQTT - [SN-002]:STATUS => RINSE
# Wed Sep 20 14:36:32 2023 - MQTT - [SN-003]:STATUS => RINSE
# Wed Sep 20 14:36:32 2023 - MQTT - [SN-004]:STATUS => RINSE
# Wed Sep 20 14:36:32 2023 - MQTT - [SN-005]:STATUS => RINSE
# Wed Sep 20 14:36:42 2023 - MQTT - [SN-001]:STATUS => SPIN
# Wed Sep 20 14:36:42 2023 - MQTT - [SN-002]:STATUS => SPIN
# Wed Sep 20 14:36:42 2023 - MQTT - [SN-003]:STATUS => RINSE
# Wed Sep 20 14:36:42 2023 - MQTT - [SN-004]:STATUS => RINSE
# Wed Sep 20 14:36:42 2023 - MQTT - [SN-005]:STATUS => RINSE
# Wed Sep 20 14:36:52 2023 - MQTT - [SN-001]:STATUS => HEATWATER
# Wed Sep 20 14:36:52 2023 - MQTT - [SN-002]:STATUS => SPIN
# Wed Sep 20 14:36:52 2023 - MQTT - [SN-003]:STATUS => SPIN
# Wed Sep 20 14:36:52 2023 - MQTT - [SN-004]:STATUS => SPIN
# Wed Sep 20 14:36:52 2023 - MQTT - [SN-005]:STATUS => SPIN
# Wed Sep 20 14:37:02 2023 - MQTT - [SN-001]:STATUS => WASH
# Wed Sep 20 14:37:02 2023 - MQTT - [SN-002]:STATUS => HEATWATER
# Wed Sep 20 14:37:02 2023 - MQTT - [SN-003]:STATUS => SPIN
# Wed Sep 20 14:37:02 2023 - MQTT - [SN-004]:STATUS => SPIN
# Wed Sep 20 14:37:02 2023 - MQTT - [SN-005]:STATUS => SPIN
# Wed Sep 20 14:37:12 2023 - MQTT - [SN-001]:STATUS => WASH
# Wed Sep 20 14:37:12 2023 - MQTT - [SN-002]:STATUS => WASH
# Wed Sep 20 14:37:12 2023 - MQTT - [SN-003]:STATUS => HEATWATER
# Wed Sep 20 14:37:12 2023 - MQTT - [SN-004]:STATUS => FILLWATER
# Wed Sep 20 14:37:12 2023 - MQTT - [SN-005]:STATUS => OFF