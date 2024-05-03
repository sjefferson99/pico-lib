from machine import Pin
from ulogging import uLogger
from uasyncio import Event, sleep_ms

class Button:
    """
    Async button class that instantiates a coroutine to watch for button pin state changes, debounces and sets appropriate asyncio events.
    """
    def __init__(self, log_level: int, GPIO_pin: int, pull_up: bool, button_name: str, button_pressed_event: Event, button_released_event: Event) -> None:
        """
        Provide buttons details to set up a logged async button watcher on a GPIO pin. Pull_up true for buttons connected to ground and False for pins connected to 3.3v
        The two event arguments should be of type asyncio.Event and used elsewhere to take action on bitton state changes.
        """
        self.log_level = log_level
        self.logger = uLogger(f"Button {GPIO_pin}", log_level)
        self.gpio = GPIO_pin
        self.pin_pull = Pin.PULL_DOWN
        if pull_up:
            self.pin_pull = Pin.PULL_UP
        self.pin = Pin(GPIO_pin, Pin.IN, self.pin_pull)
        self.name = button_name
        self.button_pressed = button_pressed_event
        self.button_released = button_released_event
   
    async def wait_for_press(self) -> None:
        """
        Async coroutine to monitor for a change in button state. On state change, input is debounced and appropriate pushed or released event is set.
        Call clear_pressed or clear_released as appropriate in function responding to button events.
        """
        self.logger.info(f"Starting button press watcher for button: {self.name}")

        while True:
            current_value = self.pin.value()
            active = 0
            while active < 20:
                if self.pin.value() != current_value:
                    active += 1
                else:
                    active = 0
                await sleep_ms(1)

            if self.pin.value() == 0:
                self.logger.info(f"Button pressed: {self.name}")
                self.button_pressed.set()
            else:
                self.logger.info(f"Button released: {self.name}")
                self.button_released.set()

    def clear_pressed(self) -> None:
        self.button_pressed.clear()
    
    def clear_released(self) -> None:
        self.button_released.clear()
    
    def get_name(self) -> str:
        """Get button name"""
        return self.name
    
    def get_pin(self) -> int:
        """Get GPIO pin connected to button"""
        return self.gpio

    def get_pull_pin(self) -> int:
        """Get pull up configuration, True is up, False is down"""
        return self.pin_pull