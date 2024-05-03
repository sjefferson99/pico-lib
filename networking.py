from utime import ticks_ms
from math import ceil
import rp2
import network
from ubinascii import hexlify
import config
from ulogging import uLogger
from led import Status_LED
import uasyncio

class Wireless_Network:
    """
    Using SSID, password and country information from config.py, provide simple methods to connect, disconnect and monitor the wireless network connection, with logging for key MAC/IP information and time to create connection.
    Has built in configurable retry and back off logic.
    Use check_network_access() to ensure the wifi is connected ahead of any network dependent code.
    Set up an async coroutine with network_monitor() to ensure the network remains connected with info log output
    Various functions for querying status including get_all_data() for JSON output compatible with APIs etc.
    Use disconnect_wifi() to ensure the wifi is not connected (ensure network_monitor coro is not running).
    Uses onboard LED to provide connectivity information:
    1 flash at 2 Hz: successful connection
    2 flashes at 2 Hz: failed connection
    Constant 4Hz flash: in backoff period before retrying connection
    """
    def __init__(self, log_level: int) -> None:
        self.logger = uLogger("WIFI", log_level)
        self.status_led = Status_LED(log_level)
        self.wifi_ssid = config.WIFI_SSID
        self.wifi_password = config.WIFI_PASSWORD
        self.wifi_country = config.WIFI_COUNTRY
        rp2.country(self.wifi_country)
        self.disable_power_management = 0xa11140
        self.led_retry_backoff_frequency = 4
        
        # Reference: https://datasheets.raspberrypi.com/picow/connecting-to-the-internet-with-pico-w.pdf
        self.CYW43_LINK_DOWN = 0
        self.CYW43_LINK_JOIN = 1
        self.CYW43_LINK_NOIP = 2
        self.CYW43_LINK_UP = 3
        self.CYW43_LINK_FAIL = -1
        self.CYW43_LINK_NONET = -2
        self.CYW43_LINK_BADAUTH = -3
        self.status_names = {
        self.CYW43_LINK_DOWN: "Link is down",
        self.CYW43_LINK_JOIN: "Connected to wifi",
        self.CYW43_LINK_NOIP: "Connected to wifi, but no IP address",
        self.CYW43_LINK_UP: "Connect to wifi with an IP address",
        self.CYW43_LINK_FAIL: "Connection failed",
        self.CYW43_LINK_NONET: "No matching SSID found (could be out of range, or down)",
        self.CYW43_LINK_BADAUTH: "Authenticatation failure",
        }
        self.ip = "Unknown"
        self.subnet = "Unknown"
        self.gateway = "Unknown"
        self.dns = "Unknown"

        self.configure_wifi()

    def configure_wifi(self) -> None:
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.config(pm=self.disable_power_management)
        self.mac = hexlify(self.wlan.config('mac'),':').decode()
        self.logger.info("MAC: " + self.mac)

    def dump_status(self):
        """Return the human readable status for the wifi chip and also output in info log"""
        status = self.wlan.status()
        self.logger.info(f"active: {1 if self.wlan.active() else 0}, status: {status} ({self.status_names[status]})")
        return status
    
    async def wait_status(self, expected_status, *, timeout=config.WIFI_CONNECT_TIMEOUT_SECONDS, tick_sleep=0.5) -> bool:
        for unused in range(ceil(timeout / tick_sleep)):
            await uasyncio.sleep(tick_sleep)
            status = self.dump_status()
            if status == expected_status:
                return True
            if status < 0:
                raise Exception(self.status_names[status])
        return False
    
    async def disconnect_wifi_if_necessary(self) -> None:
        status = self.dump_status()
        if status >= self.CYW43_LINK_JOIN and status <= self.CYW43_LINK_UP:
            await self.disconnect_wifi()
    
    async def disconnect_wifi(self) -> None:
        """Disconnect the wifi if network not needed or wanted (power save etc.)"""
        self.logger.info("Disconnecting wifi...")
        self.wlan.disconnect()
        try:
            await self.wait_status(self.CYW43_LINK_DOWN)
        except Exception as x:
            raise Exception(f"Failed to disconnect wifi: {x}")
        self.logger.info("Wifi Disconnected")
    
    def generate_connection_info(self, elapsed_ms) -> None:
        self.ip, self.subnet, self.gateway, self.dns = self.wlan.ifconfig()
        self.logger.info(f"IP: {self.ip}, Subnet: {self.subnet}, Gateway: {self.gateway}, DNS: {self.dns}")
        
        self.logger.info(f"Elapsed: {elapsed_ms}ms")
        if elapsed_ms > 5000:
            self.logger.warn(f"took {elapsed_ms} milliseconds to connect to wifi")

    async def connection_error(self) -> None:
        await self.status_led.async_flash(2, 2)

    async def connection_success(self) -> None:
        await self.status_led.async_flash(1, 2)

    async def attempt_ap_connect(self) -> None:
        self.logger.info(f"Connecting to SSID {self.wifi_ssid} (password: {self.wifi_password})...")
        await self.disconnect_wifi_if_necessary()
        self.wlan.connect(self.wifi_ssid, self.wifi_password)
        try:
            await self.wait_status(self.CYW43_LINK_UP)
        except Exception as x:
            await self.connection_error()
            raise Exception(f"Failed to connect to SSID {self.wifi_ssid} (password: {self.wifi_password}): {x}")
        await self.connection_success()
        self.logger.info("Connected successfully!")
    
    async def connect_wifi(self) -> None:
        self.logger.info("Connecting to wifi")
        start_ms = ticks_ms()
        try:
            await self.attempt_ap_connect()
        except Exception:
            raise Exception(f"Failed to connect to network")

        elapsed_ms = ticks_ms() - start_ms
        self.generate_connection_info(elapsed_ms)

    def get_status(self) -> int:
        """Return the human readable status for the wifi chip"""
        return self.wlan.status()
    
    async def network_retry_backoff(self) -> None:
        self.logger.info(f"Backing off retry for {config.WIFI_RETRY_BACKOFF_SECONDS} seconds")
        await self.status_led.async_flash((config.WIFI_RETRY_BACKOFF_SECONDS * self.led_retry_backoff_frequency), self.led_retry_backoff_frequency)

    async def check_network_access(self) -> bool:
        """Use this method to start or ensure network connectivity"""
        self.logger.info("Checking for network access")
        retries = 0
        while self.get_status() != 3 and retries <= config.WIFI_CONNECT_RETRIES:
            try:
                await self.connect_wifi()
                return True
            except Exception:
                self.logger.warn(f"Error connecting to wifi on attempt {retries + 1} of {config.WIFI_CONNECT_RETRIES + 1}")
                retries += 1
                await self.network_retry_backoff()

        if self.get_status() == 3:
            self.logger.info("Connected to wireless network")
            return True
        else:
            self.logger.warn("Unable to connect to wireless network")
            return False
        
    async def network_monitor(self) -> None:
        """Async coroutine to ensure network connectivity"""
        while True:
            await self.check_network_access()
            await uasyncio.sleep(5)
    
    def get_mac(self) -> str:
        """Get MAC address of the wifi chip"""
        return self.mac
    
    def get_wlan_status_description(self, status) -> str:
        description = self.status_names[status]
        return description
    
    def get_all_data(self) -> dict:
        """Get dictionary of all useful status data, handy for APIs"""
        all_data = {}
        all_data['mac'] = self.get_mac()
        status = self.get_status()
        all_data['status description'] = self.get_wlan_status_description(status)
        all_data['status code'] = status
        return all_data
