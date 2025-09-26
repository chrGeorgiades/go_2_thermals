import os
import socket
import json

import time

SOCKET_PATH = "/tmp/sgo2_governor.sock"
governor = ''

current_governor = ''
temp_map = {'power': 50, 'balance_performance': 65, 'performance': 85}
#governor_file_option = 'governor_option.txt'
governor_acpi = '/sys/devices/system/cpu/cpufreq/policy0/energy_performance_preference'



def apply_governor():
    global current_governor

    try:
        # Read the desired governor option from file
        with open(governor_file_option, 'r') as f:
            governor = f.read().strip()
        
        # Check if governor is in the map
        if governor != current_governor:
            if governor not in temp_map:
                print(f"Governor '{governor}' not recognized. Valid options: {list(temp_map.keys())}")
                return
            
            # Write the corresponding value to the ACPI file
            with open(governor_file_acpi, 'w') as f:
                f.write(governor)
            
            current_governor = governor

            print(f"Governor '{governor}' applied successfully.")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except PermissionError:
        print(f"Permission denied. Try running the script as root.")
        exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def bind_socket():
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(1)


def main():
    while True:
        #apply_governor()
        #time.sleep(10)
        if data:
            try:
                msg = json.loads(data.decode())
                if msg.get("command") == "set":
                    set_value(msg.get("value"))
                    conn.sendall(b"OK")
                else:
                    conn.sendall(b"Unknown command")
            except json.JSONDecodeError:
                conn.sendall(b"Invalid JSON")

        conn, _ = server.accept()
        data = conn.recv(1024)


if __name__ == "__main__":
    main()
