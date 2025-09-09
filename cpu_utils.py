import os

import conversion_utils as Conversion

# Directories
acpi_dir = '/sys/devices/system/cpu/cpufreq/policy{}/'
boost_dir = '/sys/devices/system/cpu/intel_pstate/'
governor_file = '/sys/devices/system/cpu/cpufreq/policy0/energy_performance_preference'
temperature_file = '/sys/devices/virtual/thermal/thermal_zone6/temp'
no_turbo_file = '/sys/devices/system/cpu/intel_pstate/no_turbo'


# CPU Governor Mappings
temp_map = {'power': 50, 'balance_performance': 65, 'performance': 85}
freq_map = {'power': 1.1, 'balance_performance': 2.2, 'performance': 3.4}


class CPU:
    temp_limit = 85

    freq = 0
    freq_min = 0.4
    freq_max = 3.4

    def __init__(self):
        self.read_cpu()
        self.update_readings()
        self.update_cpu_limits()
        

    def read_cpu(self):
        self.read_corecount()

    def update_readings(self):
        self.read_governor()
        self.read_turbo()
        self.read_temperature()

        self.read_freq()
        #self.read_freq_min()
        self.read_freq_max()
    

    def update_cpu_limits(self):
        self.temp_limit = temp_map.get(self.governor)
        self.freq_max = freq_map.get(self.governor)

        self.apply_freq_max(self.freq_max)


    # CPU Info
    def read_corecount(self):
        self.core_count = len(next(os.walk('/sys/devices/system/cpu/cpufreq'))[1])

    def read_governor(self):
        with open(governor_file, 'r') as f:
            self.governor = f.read().strip()

    def read_turbo(self):
        with open(no_turbo_file) as f:
            self.no_turbo = int(f.read())

    def read_temperature(self):
        try:
            with open(temperature_file) as f:
                self.temp = Conversion.temp_to_celsius(int(f.read().strip()))
        except:
            print('Failed to read CPU temperature.')


    # CPU Frequency
    def read_freq(self):
        with open('/sys/devices/system/cpu/cpufreq/policy0/cpuinfo_avg_freq') as f:
            self.freq = int(f.read())

    def read_freq_min(self):
        with open('/sys/devices/system/cpu/cpufreq/policy0/cpuinfo_min_freq') as f:
            self.min_freq = int(f.read())

    def read_freq_max(self):
        self.max_freq = freq_map.get(self.governor)

    def apply_freq_max(self, freq_max):
        self.max_freq = freq_max
        
        freq_max_c = str(Conversion.ghz_to_freq(freq_max))

        #print(freq_max)
        #print(freq_max_c)

        for i in range(self.core_count):
            policy_path = acpi_dir.format(i)
            #print(policy_path)
            
            try:
                with open(policy_path + 'scaling_max_freq', 'w') as f:
                    f.write(freq_max_c)
            except Exception as e:
                print('Error setting frequency:', e)


    def __str__(self):
        string = 'Temp: ' + str(self.temp) + '/' + str(self.temp_limit) + ' °C' + '\n' + \
                'Freq: ' + str(Conversion.freq_to_ghz(self.freq)) + '/' + str(self.max_freq) + ' Ghz'
        
        return string

    #

    # Restore Defaults
    def restore_defaults(self):
        print('Restoring defaults...')
        apply_freq(max_freq_limit)