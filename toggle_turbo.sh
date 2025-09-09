#!/bin/bash

TURBO_STATE=$(cat /sys/devices/system/cpu/intel_pstate/no_turbo)

if [ "$TURBO_STATE" -eq 1 ]; then
    echo 0 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo
    notify-send "Turbo Boost Enabled"
else
    echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo
    notify-send "Turbo Boost Disabled"
fi
