import os, socket

SOCKET_PATH = "/tmp/sgo2_governor.sock"

temp_map = {'power': 50, 'balance_performance': 65, 'performance': 85}
governor_cycle = ['power', 'balance_performance', 'performance']

governor_acpi = '/sys/devices/system/cpu/cpufreq/policy0/energy_performance_preference'


# Connect to the socket 
def connect_socket():
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCKET_PATH)

    print(f"Client connected to ", SOCKET_PATH)

    return client


# Toggle a governor change for the CPU
def get_next_governor():
    try:
        current_governor = ''
        
        with open(governor_acpi, 'r') as f:
            current_governor = f.read().strip()
            print('current_governor:', current_governor)
        
        if current_governor not in temp_map:
            print(f"Governor '{current_governor}' not recognized. Valid options: {list(temp_map.keys())}")
            current_governor = 'performance'

        index = governor_cycle.index(current_governor)
        next_index = (index + 1) % len(governor_cycle)
        governor = governor_cycle[next_index]

        client = connect_socket()

        try:
            client.sendall(governor.encode("utf-8"))
            print(f"Sent to server: {governor.encode("utf-8")}")
        finally:
            client.close()
        
        print(f"Governor '{governor}' applied successfully.")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except PermissionError:
        print(f"Permission denied. Try running the script as root.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



def main():
    get_next_governor()


if __name__ == "__main__":
    main()
