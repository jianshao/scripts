from src import mobileController
from src.util import adbCmd
from config import config

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    process_list = []
    for device in config["devices"]:
        # 检查设备是否可用
        serial = device["serial"]
        available = adbCmd.check_device_available(serial)
        if not available:
            continue

        channel = device["channel"]
        p = mobileController.MobileController(serial, 'com.tencent.tmgp.sgame', '.SGameActivity', channel)
        p.start()
        process_list.append(p)

    for p in process_list:
        p.join()

