# coding: utf-8

import time
# noinspection PyUnresolvedReferences
import RPi.GPIO as GPIO

# Set GPIO naming convention
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class Buttons:

    def __init__(self, config, companion, tally_blinker, logger):
        # Define GPIO ports and other properties for buttons
        self.configure_button(config)
        self.companion = companion
        self.state = 1
        self.tally = tally_blinker
        self.visual_echo = False
        self.logger = logger

        GPIO.setup(config['port'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        if config.get('mode', 'Normal') == 'PTT':
            GPIO.add_event_detect(self.port, GPIO.BOTH, callback=self.button_action, bouncetime=40)
        else:
            GPIO.add_event_detect(self.port, GPIO.FALLING, callback=self.button_pressed, bouncetime=150)

    def configure_button(self, config):
        self.config = config
        self.name = config['name']
        self.port = config['port']
        self.reverse = config.get('reverse', 0)
        self.bank = config.get('bank')
        self.number = config.get('number')

    def button_action(self, port):
        gpio_value = GPIO.input(port)
        # self.logger.info(f"Reverse {self.reverse} on port {port} with value {gpio_value}")
        if gpio_value != self.reverse:
            self.logger.info(f"Button {self.config['name']} on port {port} was released")
            self.state = 1
            self.execute_action('up')
        else:
            self.logger.info(f"Button {self.config['name']} on port {port} was pressed")
            self.state = 0
            self.execute_action('down')


    def button_pressed(self, port):
        self.logger.info(f"Button {self.config['name']} on port {port} was pressed")
        self.execute_action(None)

    def button_web_test(self):
        self.logger.info("Enter TEST TOGGLE")
        if self.state == 1:
            self.logger.info(f"Test Button {self.config['name']} was released")
            self.state = 0
            self.execute_action('up')
        else:
            self.logger.info(f"Test Button {self.config['name']} was pressed")
            self.state = 1
            self.execute_action('down')

    def execute_action(self, action):
        self.companion.press_key(self.config.get('bank'), self.config.get('number'), action)

        if self.visual_echo:
            if self.tally:
                self.tally.set_tally(0, 'pvw')
                time.sleep(0.1)
                self.tally.set_tally(0, 'off')


