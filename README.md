# Pico-lib
## Overview
Libraries I often use in my own pico projects.

## Libraries
### Button
Class for buttons that includes debouncing and an async event generator on button push and release.

### LED
Drive LEDs on GPIO pins (including onboard LED for W or standard), with sync and async flashing functions.

### Networking
Reliably set up wifi networking including network status checker and connection monitor async coroutine. Run check_network_access() to connect or ensure network access with basic configuration in config.py.

### uLogging
Simple alternative to logging.py that has various log levels, module name and free memory output on each log line.