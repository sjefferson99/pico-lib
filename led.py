"""
Built against Pimoroni Micropython version: v1.22.2 (https://github.com/pimoroni/pimoroni-pico/releases/download/v1.22.2/pimoroni-picow-v1.22.2-micropython.uf2)
"""

from time import sleep
from machine import Pin
from asyncio import sleep as async_sleep
from ulogging import uLogger
import config
from machine import Pin, PWM

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

class Light:
    """
    Module for controlling LED lighting (or any lighting that supports PWM for dimming) via GPIO.
    Includes methods for getting and setting on/off and brightness and a get all data method for APIs.
    """
    def __init__(self, log_level: int) -> None:
        self.log_level = log_level
        self.logger = uLogger("Light", log_level)
        self.logger.info("Init light")
        self.pin = config.led_pin
        self.max_pwm_duty = 65535
        self.pwm_pin = PWM(Pin(self.pin, Pin.OUT))
        self.pwm_pin.freq(1000)
        self.brightness_pc = config.default_brightness_pc
        self.off()

    def init_service(self) -> None:
        self.logger.info("Init light management (stub)")
    
    def brightness_to_corrected_duty(self, brightness: float) -> float:
        decimal = brightness / 100
        square = decimal * decimal
        return square
    
    def off(self) -> None:
        """Set brightness to 0"""
        self.logger.info("Turning light off")
        self.pwm_pin.duty_u16(0)

    def on(self) -> None:
        """Set brightness to maximum"""
        self.logger.info("Turning light on")
        duty = int(self.max_pwm_duty * self.brightness_to_corrected_duty(self.brightness_pc))
        self.pwm_pin.duty_u16(duty)
    
    def set_brightness_pc(self, pc_brightness: float) -> None:
        """Set light to specific brightness as a percentage"""
        self.brightness_pc = pc_brightness
        self.logger.info(f"Setting light to {pc_brightness}%")
        duty = int(self.max_pwm_duty * self.brightness_to_corrected_duty(pc_brightness))
        self.pwm_pin.duty_u16(duty)
        
    def get_state(self) -> bool:
        "Is the light on or off"
        state = self.pwm_pin.duty_u16()
        if state > 0:
            return True
        else:
            return False
    
    def get_brightness_pc(self) -> float:
        "Get light brightness in percent"
        return self.brightness_pc
    
    def get_all_data(self) -> dict:
        """All useful data about the light"""
        all_data = {}
        all_data['brightness pc'] = self.get_brightness_pc()
        all_data['state'] = self.get_state()
        return all_data
    