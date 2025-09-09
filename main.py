
import time
import subprocess
import atexit

import cpu_utils


polling_delay = 5


if __name__ == "__main__":
    #atexit.register(optimizer_utils.restore_defaults)
    
    cpu = cpu_utils.CPU()
    print(cpu)

    while True:
        cpu.update_readings()
        cpu.update_cpu_limits()
        print(cpu)
        time.sleep(polling_delay)

