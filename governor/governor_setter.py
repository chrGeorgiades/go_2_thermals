import time

current_governor = ''
temp_map = {'power': 50, 'balance_performance': 65, 'balance_power': 65, 'performance': 85}
governor_file_option = 'governor_option.txt'
governor_file_acpi = '/sys/devices/system/cpu/cpufreq/policy0/energy_performance_preference'

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


def main():
    while True:
        apply_governor()
        time.sleep(10)

if __name__ == "__main__":
    main()
