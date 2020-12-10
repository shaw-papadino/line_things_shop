import asyncio
import time
from bleak import BleakClient, BleakScanner

WRITE_CHARACTERISTIC_UUID = "e9062e71-9e62-4bc6-b0d3-35cdcd9b027b"
mac_addr = "DA5D8E4A-6A34-4D71-919D-D9CD26EA90A5"

async def run(address, loop):
    # device = await BleakScanner.find_device_by_address(address)
    async with BleakClient(address, loop=loop) as client:
        x = await client.is_connected()
        print("Connected: {0}".format(x))
        write_value = bytearray(b"1")
        await client.write_gatt_char(WRITE_CHARACTERISTIC_UUID, write_value)
        print("write")
        # 5秒後に終了
        await asyncio.sleep(5.0, loop=loop)

if __name__=="__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(mac_addr, loop))

