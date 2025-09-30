import os,socket
import threading
import time

import conversion_utils as Conversion

DEBUG = False

# Directories
acpi_dir = '/sys/devices/system/cpu/cpufreq/policy{}/'
boost_dir = '/sys/devices/system/cpu/intel_pstate/'

governor_file = '/sys/devices/system/cpu/cpufreq/policy0/energy_performance_preference'

temperature_file = '/sys/devices/virtual/thermal/thermal_zone6/temp'
freq_file = '/sys/devices/system/cpu/cpufreq/policy0/scaling_cur_freq'

no_turbo_file = '/sys/devices/system/cpu/intel_pstate/no_turbo'


# CPU Governor Mappings
temp_map = {'power': 55, 'balance_performance': 65, 'performance': 85}
freq_map = {'power': 1.4, 'balance_performance': 2.6, 'performance': 3.4}

governor_cycle = ['power', 'balance_performance', 'performance']

SOCKET_PATH = "/tmp/sgo2_governor.sock"

polling_delay = 1   # (seconds)

class CPU:
    temp = 0                    # Current CPU temperature
    temp_error = 3              # The difference from the temp_limit in order for the controller to kick in
    temp_limit = 85             # Temperature limit based on governor

    freq = 0                    # Current Frequency
    freq_min = 0.7              # Minimum Frequency
    freq_max = 3.4              # Maximum frequency based on governor
    freq_max_adjusted = 3.4     # Maximum Frequency after thermal throttling
    freq_step = 0.3             # Step in frequency reduction/increase due to thermal limit

    governor = 'performance'

    is_running = True
    controller_mutex = threading.Lock()


    def __init__(self):
        self.read_cpu()
        self.update_readings()

        # Main CPU controller loop, responsible for updating the frequency bounds
        # based on the CPU thermals
        self.cpu_controller_thread = threading.Thread(target=self.cpu_controller_loop, daemon=True)
        self.cpu_controller_thread.start()

        # Start a listening loop, reads and applies a certain governor.
        self.socket_thread = threading.Thread(target=self.socket_listen_loop, daemon=True)
        self.socket_thread.start()

        print('CPU controller - Initialized')


    def cpu_controller_loop(self):
        while self.is_running:
            with self.controller_mutex:
                self.update_readings()
                self.update_freq_limit()

                #self.update_readings()
            
            time.sleep(polling_delay)
            #print('hello world')

    
    # Controls CPU frequency based on the temperature
    def update_freq_limit(self):
   
        # CPU temperature exceeds thermal limit
        if self.temp > self.temp_limit + self.temp_error:

            if self.freq_max_adjusted > self.freq_min:
                self.freq_max_adjusted = round(self.freq_max_adjusted - self.freq_step, 1)

                if self.freq_max_adjusted < self.freq_min:
                    self.freq_max_adjusted = self.freq_min

                self.apply_freq_max()
                #self.read_freq()
                #print(self.freq_max_adjusted)
                self.freq = self.freq_max_adjusted
                #print(self.freq)

        
        # CPU temperature within thermal limit
        elif self.temp < self.temp_limit - self.temp_error:
            
            # Allowed CPU frequency lower than the lower bound Frequency limit
            if self.freq_max_adjusted < self.freq_max:
                self.freq_max_adjusted = round(self.freq_max_adjusted + self.freq_step, 1)
                
                if self.freq_max_adjusted > self.freq_max:
                    self.freq_max_adjusted = self.freq_max

                self.apply_freq_max()
                #self.read_freq()
                #print(self.freq_max_adjusted)
                self.freq = self.freq_max_adjusted
                #print(self.freq)



    def apply_freq_max(self):        
        freq_max_c = str(Conversion.ghz_to_freq(self.freq_max_adjusted))

        # if self.freq > self.freq_max_adjusted:
        #     self.freq = round(self.freq_max_adjusted, 1)

        for i in range(self.core_count):
            policy_path = acpi_dir.format(i)
            #print(policy_path)
            
            try:
                with open(policy_path + 'scaling_max_freq', 'w') as f:
                    f.write(freq_max_c)
            except Exception as e:
                print('Error setting frequency:', e)


    def apply_governor(self, target_governor):
        self.governor = target_governor

        for i in range(self.core_count):
            policy_path = acpi_dir.format(i)
            #print(policy_path)
            
            try:
                with open(policy_path + 'energy_performance_preference', 'w') as f:
                    f.write(self.governor)
            except Exception as e:
                print('Error setting frequency:', e)

        

    
    def toggle_governor(self):
        index = governor_cycle.index(self.governor)
        next_index = (index + 1) % len(governor_cycle)
        governor = governor_cycle[next_index]

        self.apply_governor(governor)
        self.apply_controller_limits()


    def apply_controller_limits(self):
        self.freq_max = freq_map.get(self.governor)
        self.freq_max_adjusted = self.freq_max
        self.temp_limit = temp_map.get(self.governor)

        self.apply_freq_max()


    # Socket for listening to Governor changes
    def socket_listen_loop(self):
        self.server = self.bind_socket()

        while self.is_running:
            try:
                conn, _ = self.server.accept()
                print("Client connected.")
                self.handle_client(conn)
            except Exception as e:
                print(f"Error in listen_loop: {e}")

    
    # Read instructions from socket 
    def handle_client(self, conn):
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
            
                print(f"Received: {data.decode()}")

                # Apply changes to controller based on incoming instructions from Socket
                with self.controller_mutex:
                    self.toggle_governor()


    # Create Socket. Used for giving instructions to this program when daemonized
    def bind_socket(self):
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(SOCKET_PATH)
        server.listen(1)

        os.chmod(SOCKET_PATH, 0o666) # This allows anyone to connect to the socket

        print(f"Server listening on {SOCKET_PATH}")

        return server


    # Read current CPU metrics (Temperature, Operating Frequency)
    def update_readings(self):
        self.read_temperature()
        self.read_freq()


    def read_temperature(self):
        try:
            with open(temperature_file) as f:
                self.temp = Conversion.temp_to_celsius(int(f.read().strip()))
        except:
            print('Failed to read CPU temperature.')

    def read_freq(self):
        with open(freq_file) as f:
            self.freq = Conversion.freq_to_ghz(int(f.read()))


    # Read initial CPU configuration
    def read_cpu(self):
        self.read_corecount()
        self.read_governor()

        #self.read_turbo()
        

    def read_corecount(self):
        self.core_count = len(next(os.walk('/sys/devices/system/cpu/cpufreq'))[1])

    def read_governor(self):
        with open(governor_file, 'r') as f:
            governor = f.read().strip()

        if self.governor != governor:
            self.governor = governor
            self.apply_controller_limits()


    def read_turbo(self):
        with open(no_turbo_file) as f:
            self.no_turbo = int(f.read())




    def __str__(self):
        #string ='Governor: ' + self.governor + '\n' + \
        string = 'Temp: ' + str(self.temp) + '/' + str(self.temp_limit) + ' °C' + ' | ' + \
                'Freq: ' + str(self.freq) + '/' + str(self.freq_max_adjusted) + ' Ghz\n'
        
        return string


    # Restore Defaults
    def restore_defaults(self):
        print('Restoring defaults...')
        #self.apply_freq_max(freq_map.get('performance'))
        self.apply_governor('performance')
