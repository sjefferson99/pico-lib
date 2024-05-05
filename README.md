# Pico-lib
## Overview
Libraries I often use in my own pico projects.

These are all built against Pimoroni micropython firwmare [v1.22.2](https://github.com/pimoroni/pimoroni-pico/releases/download/v1.22.2/pimoroni-picow-v1.22.2-micropython.uf2) unless otherwise specified in the module, although not all require the Pimoroni elements. Ensure you are using a similar micropython version if not leveraging any Pimoroni custom elements.

### VS Code
I use VS Code for better or worse, custom pylance stubs for Pimoroni modules are available here: [https://github.com/pimoroni/pimoroni-pico-stubs](https://github.com/pimoroni/pimoroni-pico-stubs)

### Config.py
Config.py contains the configuration required to drive the libraries below with comments linking each config to the appropriate library.

## Libraries
### BME280
Simple wrapper around BME280 pressure, humidity and temperature sensor using I2C details from config.py.

### Button
Buttons that includes debouncing and an async event generator on button push and release.

### LED
#### Light
PWM based dimmable control over LED lighting strips

#### Status_LED
Drive LEDs on GPIO pins (including onboard LED for W or standard), with sync and async flashing functions.

### Networking
Reliably set up wifi networking including network status checker and connection monitor async coroutine. Run check_network_access() to connect or ensure network access with basic configuration in config.py.

### Open-Meteo
Use dependent uaiohttpclient library ([https://pypi.org/project/micropython-uaiohttpclient/](https://pypi.org/project/micropython-uaiohttpclient/)) to query the Open-Meteo API and in this example request local humidity information and process the returned JSON before returning the information in a dict.

### uLogging
Simple alternative to logging.py that has various log levels, module name and free memory output on each log line.