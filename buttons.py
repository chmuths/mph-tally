# coding: utf-8

from threading import Timer
import RPi.GPIO as GPIO

# Set GPIO naming convention
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class Buttons:

    def __init__(self, config, videohub):
        # Define GPIO ports associated to each moving head feature and other properties
        self.config = config
        self.name = config['name']
        self.videohub = videohub
        self.toggle_index = -1

        GPIO.setup(config['port'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(config['port'], GPIO.FALLING, callback=self.button_action, bouncetime=250)

    def configure_button(self, action, matrix_out, matrix_in):
        self.config['action'] = action
        self.config['matrix_out'] = matrix_out
        self.config['matrix_in'] = matrix_in

    def button_action(self, port):
        print(f"Button {self.config['name']} on port {port} was pressed")
        # GPIO.remove_event_detect(self.config['port'])
        self.execute_action()
        # GPIO.add_event_detect(self.config['port'], GPIO.FALLING, callback=self.button_action, bouncetime=400)

    def execute_action(self):
        action = self.config['action']
        print(f"action is {action}")
        if action == 'switch':
            self.videohub.connect(self.config['matrix_out'], self.config['matrix_in'][0])
        elif action == 'toggle':
            self.toggle_index += 1
            if self.toggle_index >= len(self.config['matrix_in']):
                self.toggle_index = 0
            self.videohub.connect(self.config['matrix_out'], self.config['matrix_in'][self.toggle_index])
