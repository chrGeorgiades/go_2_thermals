import os
import time
import subprocess

import atexit

# Directories
acpi_dir = '/sys/devices/system/cpu/cpufreq/policy*/'
boost_dir = '/sys/devices/system/cpu/intel_pstate/'

governor_dir = '/sys/devices/system/cpu/cpufreq/policy0/energy_performance_preference'

config_file = 'config.txt'


# Temperature
temperature_file = '/sys/devices/virtual/thermal/thermal_zone*/temp'
temp_error = 3

keep_below_temperature=75
actual_temperature=0

temp_map = {'power': 50, \
            'balance_performance': 60, \
            'performance' : 75}




# CPU Frequencies
core_count = int(subprocess.check_output(['find /sys/devices/system/cpu/cpufreq/policy* -maxdepth 1 -type d | wc -l'], shell=True))
print('core_count:', core_count)

cur_freq=0

min_freq=0
min_freq_limit=int(subprocess.check_output(['cat /sys/devices/system/cpu/cpufreq/policy0/cpuinfo_min_freq'], shell=True))

max_freq=0
max_freq_limit=int(subprocess.check_output(['cat /sys/devices/system/cpu/cpufreq/policy0/cpuinfo_max_freq'], shell=True))

no_turbo=int(subprocess.check_output(['cat /sys/devices/system/cpu/intel_pstate/no_turbo'], shell=True))


polling_delay=10


def read_config():
    global polling_delay, keep_below_temperature

    #print('file: ', config_file)
    with open(config_file) as f:
        for line in f:
            #print('line: ', line)
            if not '#' in line:
                #if 'keep_below_temperature' in line:
                #    keep_below_temperature=int(line.split('=')[1])
                #elif 'polling_delay' in line:
                if 'polling_delay' in line:
                    polling_delay=int(line.split('=')[1])


ghz_ratio = 1000000
dec_acc = 2
def freq_to_ghz(freq):
    return round(freq/ghz_ratio, dec_acc)


celsius_ratio = 1000
def temp_to_celsius(temp):
    return int(temp/celsius_ratio)


def get_cpu_freq():
    global cur_freq, min_freq, max_freq, max_freq_limit, no_turbo, keep_below_temperature, governor

    print('\t', 'Allowed Maximum Frequency:\t' + str(freq_to_ghz(max_freq_limit)) + '\tNo Turbo:\t' + str(no_turbo))

    governor_dir_f = open(governor_dir, 'r')
    governor = governor_dir_f.read().strip()
    
    
    #print('keep_below_temperature:', keep_below_temperature)

    for i in range(core_count):
        #print(i)
        acpi_dir_cur = acpi_dir.replace('*', str(i))
        cur_freq_f = open(acpi_dir_cur+'scaling_cur_freq', 'r')
        cur_freq = int(cur_freq_f.read())
        cur_freq_f.close()

        min_freq_f = open(acpi_dir_cur+'scaling_min_freq', 'r')
        min_freq = int(min_freq_f.read())
        min_freq_f.close()

        max_freq_f = open(acpi_dir_cur+'scaling_max_freq', 'r')
        max_freq = int(max_freq_f.read())
        max_freq_f.close()


        
        no_turbo=int(subprocess.check_output(['cat /sys/devices/system/cpu/intel_pstate/no_turbo'], shell=True))

        if no_turbo == 0:
            max_freq_limit=int(subprocess.check_output(['cat /sys/devices/system/cpu/cpufreq/policy0/cpuinfo_max_freq'], shell=True))
        elif no_turbo == 1:
            max_freq_limit=int(subprocess.check_output(['cat /sys/devices/system/cpu/cpufreq/policy0/base_frequency'], shell=True))

        print('CPU [Core '+str(i)+']:\t', str(freq_to_ghz(cur_freq))+' Ghz', '\t[' + str(freq_to_ghz(min_freq)) + '/' + str(freq_to_ghz(max_freq)) + ']')
        
                # Variable sets
        # print('min_freq:', min_freq)
        # print('cur_freq:', cur_freq)
        # print('max_freq:', max_freq)
        # print('max_freq_limit:', max_freq_limit)
        # print('no_turbo:', no_turbo)
        # print('governor:', governor)
        # print('...')
    






#/sys/devices/system/cpu/cpufreq/policy0/scaling_cur_freq
#/sys/devices/system/cpu/cpufreq/policy0/scaling_driver
#/sys/devices/system/cpu/cpufreq/policy0/scaling_governor
#/sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq
#/sys/devices/system/cpu/cpufreq/policy0/scaling_min_freq



def get_temperature():
    global actual_temperature
    try:
        sensor_temps = subprocess.check_output(['cat ' + temperature_file], shell=True)
        sensor_temps = [temp_to_celsius(int(s)) for s in sensor_temps.split()]
        actual_temperature = max(sensor_temps)

        #print('sensor_temps:', sensor_temps)
        print('CPU Temp:', str(actual_temperature)+'/'+str(keep_below_temperature), '\tsensor_temps:', sensor_temps)
    except:
        print('Failed to get core temperature. Using previous...')




def apply_freq(target_freq):
    for i in range(core_count):
        print('core', i)
        acpi_dir_cur = acpi_dir.replace('*', str(i))
        try:
            max_freq_f = open(acpi_dir_cur+'scaling_max_freq', 'w')
            print('writing...', target_freq)
            max_freq_f.write(str(target_freq))
            max_freq_f.close()
        except e:
            print('error during max_freq:', e)


def lower_max_freq():
    global max_freq

    # print('min_freq_limit:', min_freq_limit)
    # print('max_freq:', max_freq)
    # print('max_freq_limit:', max_freq_limit)
    # print('...')

    freq_change_offset = int((max_freq_limit-min_freq_limit)*0.10)
    target_freq = max_freq - freq_change_offset
    
    if target_freq < min_freq_limit:
        target_freq = min_freq_limit
    if target_freq >= min_freq_limit and target_freq != max_freq:
        print('freq_change_offset:', freq_change_offset)
        print('lower target_freq:', target_freq)
        apply_freq(target_freq)


def raise_max_freq():
    global max_freq

    # print('min_freq_limit:', min_freq_limit)
    # print('max_freq:', max_freq)
    # print('max_freq_limit:', max_freq_limit)
    # print('...')

    freq_change_offset = int((max_freq_limit-min_freq_limit)*0.10)
    target_freq = max_freq + freq_change_offset
    
    if target_freq > max_freq_limit:
        target_freq = max_freq_limit
    if target_freq <= max_freq_limit and target_freq != max_freq:
        print('freq_change_offset:', freq_change_offset)
        print('raise target_freq:', target_freq)
        apply_freq(target_freq)
    


def calculate_cpu_freq():
    print('keep_below_temperature:', keep_below_temperature, 'actual_temperature:', actual_temperature)

    if actual_temperature > keep_below_temperature + temp_error:
        lower_max_freq()
    if actual_temperature < keep_below_temperature - temp_error:
        raise_max_freq()


def restore_defaults():
    print('restoring defaults...')
    apply_freq(max_freq_limit)



print('polling_delay:', polling_delay)
atexit.register(restore_defaults)
#read_config()
while True:
    #read_config()
    #print()
    get_cpu_freq()
    get_temperature()
    print('...')
    calculate_cpu_freq()

    time.sleep(polling_delay)


