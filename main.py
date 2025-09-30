
import time
import subprocess
import atexit

import cpu_utils


polling_delay = 1   # (seconds)


if __name__ == "__main__":   
    cpu = cpu_utils.CPU()
    #print(cpu)

    atexit.register(cpu.restore_defaults)

    while True:
        print(cpu, flush=True)
        time.sleep(polling_delay)

