current_governor = ''
temp_map = {'power': 50, 'balance_performance': 65, 'performance': 85}
governor_cycle = ['power', 'balance_performance', 'performance']
governor_file_option = '/home/chr/Documents/workshop/sgo2-optimizer/governor/governor_option.txt'

def get_next_governor():
    try:
        # Read the desired governor option from file
        with open(governor_file_option, 'r') as f:
            current_governor = f.read().strip()
        
        # Check if governor is in the map
        if current_governor not in temp_map:
            print(f"Governor '{current_governor}' not recognized. Valid options: {list(temp_map.keys())}")
            current_governor = 'performance'

        index = governor_cycle.index(current_governor)
        next_index = (index + 1) % len(governor_cycle)
        governor = governor_cycle[next_index]

        with open(governor_file_option, 'w') as f:
            f.write(governor)
        
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
