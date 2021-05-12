# coding: utf-8

from threading import Timer
import time
# noinspection PyUnresolvedReferences
import RPi.GPIO as GPIO

# Set GPIO naming convention
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class Buttons:

    def __init__(self, config, companion, tally_blinker, logger):
        # Define GPIO ports and other properties for buttons
        GPIO.setup(config['port'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.logger = logger
        self.configure_button(config)
        self.companion = companion
        self.debounce_counter = 0
        self.port = config['port']
        self.reverse = config.get('reverse', 0)
        self.state = 0 if self.reverse else 1
        self.state_str = "up"
        self.tally = tally_blinker
        self.visual_echo = False

        self.run = True
        self.trigger_timer()

    def trigger_timer(self):
        if self.run:
            t = Timer(0.01, self.debounce)
            t.start()

    def debounce(self):
        gpio_value = GPIO.input(self.port)
        if self.state != gpio_value:
            self.debounce_counter += 1
            if self.debounce_counter > 3:
                self.state = gpio_value
                self.debounce_counter = 0
                self.button_action()
        self.trigger_timer()

    def configure_button(self, config):
        self.config = config
        self.name = config['name']
        self.bank = config.get('bank')
        self.number = config.get('number')

    def button_action(self):
        # self.logger.info(f"Reverse {self.reverse} on port {port} with value {gpio_value}")
        if self.state != self.reverse:
            self.logger.info(f"Button {self.config['name']} on port {self.port} was released")
            self.state_str = 'up'
            self.execute_action()
        else:
            self.logger.info(f"Button {self.config['name']} on port {self.port} was pressed")
            self.state_str = 'down'
            self.execute_action()

    def button_web_test(self):
        self.logger.info("Enter TEST TOGGLE")
        if self.state_str == "down":
            self.logger.info(f"Test Button {self.config['name']} was released")
            self.state_str = 'up'
            self.execute_action()
        else:
            self.logger.info(f"Test Button {self.config['name']} was pressed")
            self.state_str = 'down'
            self.execute_action()

    def execute_action(self):
        self.companion.press_key(self.config.get('bank'), self.config.get('number'), self.state_str)

        if self.visual_echo:
            if self.tally:
                self.tally.set_tally(0, 'pvw')
                time.sleep(0.1)
                self.tally.set_tally(0, 'off')


