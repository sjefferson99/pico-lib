"""
Built against Pimoroni Micropython version: v1.22.2 (https://github.com/pimoroni/pimoroni-pico/releases/download/v1.22.2/pimoroni-picow-v1.22.2-micropython.uf2)
"""

from time import sleep
from machine import Pin
from asyncio import sleep as async_sleep
from ulogging import uLogger

class Status_LED:
    """
    Instantiate an LED on a GPIO pin or leave pin unset for onboard LED.
    Info log level output of state changes.
    Supports sync and async flash functions taking count and frequency arguments.
    """
    def __init__(self, log_level: int, gpio_pin: int = -1) -> None:
        """
        Provide log output level and GPIO pin attached to LED, leave GPIO pin unset for onboard LED.
        """
        self.logger = uLogger("Status_LED", log_level)
        if gpio_pin > -1:
            self.status_led = Pin(gpio_pin, Pin.OUT)
            self.pin_id = gpio_pin
        else:
            self.status_led = Pin("LED", Pin.OUT)
            self.pin_id = "LED"
    
    def on(self) -> None:
        """"Turn the LED on"""
        self.logger.info(f"Pin {self.pin_id}: LED on")
        self.status_led.on()

    def off(self) -> None:
        """"Turn the LED off"""
        self.logger.info(f"Pin {self.pin_id}: LED off")
        self.status_led.off()

    async def async_flash(self, count: int, hz: float) -> None:
        """Flash the LED a number of times at a given frequency using async awaits on the sleep function."""
        self.off()
        sleep_duration = (1 / hz) / 2
        for unused in range(count):
            await async_sleep(sleep_duration)
            self.on()
            await async_sleep(sleep_duration)
            self.off()
    
    async def async_constant_flash(self, hz: float) -> None:
        """
        Flash the LED constantly at a given frequency using async awaits on the sleep function.
        This should be started by task = asyncio.create_task() and cancelled with task.cancel().
        """
        self.off()
        sleep_duration = (1 / hz) / 2
        while True:
            await async_sleep(sleep_duration)
            self.on()
            await async_sleep(sleep_duration)
            self.off()
    
    def flash(self, count: int, hz: float) -> None:
        """Flash the LED a number of times at a given frequency using standrad blocking sleep function."""
        self.off()
        sleep_duration = (1 / hz) / 2
        for unused in range(count):
            sleep(sleep_duration)
            self.on()
            sleep(sleep_duration)
            self.off()