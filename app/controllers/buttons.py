# coding: utf-8

import time
# noinspection PyUnresolvedReferences
import RPi.GPIO as GPIO

# Set GPIO naming convention
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class Buttons:

    def __init__(self, config, companion, tally_blinker):
        # Define GPIO ports associated to each moving head feature and other properties
        self.configure_button(config)
        self.companion = companion
        self.state = 'up'
        self.tally = tally_blinker
        self.visual_echo = False

        GPIO.setup(config['port'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        if config.get('mode', 'Normal') == 'PTT':
            GPIO.add_event_detect(self.port, GPIO.BOTH, callback=self.button_action, bouncetime=250)
        else:
            GPIO.add_event_detect(self.port, GPIO.FALLING, callback=self.button_pressed, bouncetime=250)

    def configure_button(self, config):
        self.config = config
        self.name = config['name']
        self.port = config['port']
        self.bank = config.get('bank', 1)
        self.number = config.get('number', 2)

    def button_action(self, port):
        if GPIO.input(port):
            print(f"Button {self.config['name']} on port {port} was released")
            self.state = 'up'
            self.execute_action('up')
        else:
            print(f"Button {self.config['name']} on port {port} was pressed")
            self.state = 'down'
            self.execute_action('down')

    def button_pressed(self, port):
        print(f"Button {self.config['name']} on port {port} was pressed")
        # GPIO.remove_event_detect(self.config['port'])
        self.execute_action(None)
        # GPIO.add_event_detect(self.config['port'], GPIO.FALLING, callback=self.button_action, bouncetime=250)

    def button_toggle(self):
        print("Enter TOGGLE")
        if self.state == 'down':
            print(f"Test Button {self.config['name']} was released")
            self.state = 'up'
            self.execute_action('up')
        else:
            print(f"Test Button {self.config['name']} was pressed")
            self.state = 'down'
            self.execute_action('down')

    def execute_action(self, action):
        self.companion.press_key(self.bank, self.number, action)

        if self.visual_echo:
            if self.tally:
                self.tally.set_tally(0, 'pvw')
                time.sleep(0.1)
                self.tally.set_tally(0, 'off')


