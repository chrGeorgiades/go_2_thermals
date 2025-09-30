# Go 2 Thermals

A CPU frequency / thermal control service, originally designed for the Surface Go 2. I found other available packages like thermald to not be working properly and being convoluted, thus I created this CPU control module. 

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Features
- Protects CPU from shutting down due to overheating.
- Reduces battery usage by limiting CPU power consumption.
- Controls CPU max frequency depending on governor setting.
- Dynamically adjusts CPU max frequency based on preset thermal limits, set by the governor.

## Installation
Install service by editing and copying the provided systemctl template file:
```
cp sgo2.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable sgo2.service
```

## Usage
Run service manually:
```
python3 main.py
```


The provided governor_toggle.py script allows to change the governor cycling through the following options; power, balanced, and performance. It can be used by polybar or dmenu as a way to control the CPU governor:
```
python3 governor_toggle.py
```

## License
MIT License.
