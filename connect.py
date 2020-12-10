import asyncio

from bleak import BleakClient, BleakScanner


async def print_services(mac_addr: str):
    device = await BleakScanner.find_device_by_address(mac_addr)
    print(device)
    async with BleakClient(device) as client:
        svcs = await client.get_services()
        print("Services:", svcs)


mac_addr = "DA5D8E4A-6A34-4D71-919D-D9CD26EA90A5"
loop = asyncio.get_event_loop()
loop.run_until_complete(print_services(mac_addr))
