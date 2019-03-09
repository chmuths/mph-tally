# coding: utf-8

import RPi.GPIO as GPIO
import time
import json
import os.path
from flask import Flask, render_template, send_file, request, jsonify

default_dir_pictures = ['left_up_bw', 'up_bw', 'right_up_bw',
                        'left_bw', 'stop_bw', 'right_bw',
                        'left_down_bw', 'down_bw', 'right_down_bw']
default_speed_pictures = ['slow_bw', 'medium_bw', 'fast_bw']

# Get config file from same folder than this module
folder_name = os.path.dirname(__file__)
path = os.path.join(folder_name, 'config.json')
with open(path, 'r') as config_file:
    hw_conf = json.load(config_file)

def save_config(hw_config):
    # Get config file from same folder than this module
    folder_name = os.path.dirname(__file__)
    path = os.path.join(folder_name, 'config.json')
    with open(path, 'w') as config_file:
        json.dump(hw_config, config_file)


# Define GPIO ports associated to each moving head feature and other properties
heads=[]
head_id = 0
for head in hw_conf['heads']:
    heads = heads + [{'name': head['name'],
                      'id': head_id,
                      'left': head['ports']['left'],
                      'right': head['ports']['right'],
                      'up': head['ports']['up'],
                      'down': head['ports']['down'],
                      'slow': head['ports']['slow'],
                      'medium': 0,
                      'has_medium': False,
                      'current_dir': 'stop',
                      'current_speed': 'slow',
                      'dir_pictures': default_dir_pictures.copy(),
                      'speed_pictures': default_speed_pictures.copy()}]
    if 'medium' in head['ports']:
        heads[head_id]['has_medium'] = True
        heads[head_id]['medium'] = head['ports']['medium']
    head_id += 1

print(heads)

tallies=[]
tally_id = 0
for tally in hw_conf['tallies']:
    tallies = tallies + [{'name': tally['name'],
                          'id': tally_id,
                          'pgm': tally['pgm'],
                          'pvw': tally['pvw'],
                          'current_status': 'OFF'}]
    tally_id += 1

print(tallies)

# Set GPIO naming convention
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Initialize ports
for head in heads:
    GPIO.setup(head['left'], GPIO.OUT)
    GPIO.setup(head['right'], GPIO.OUT)
    GPIO.setup(head['up'], GPIO.OUT)
    GPIO.setup(head['down'], GPIO.OUT)
    GPIO.setup(head['slow'], GPIO.OUT)
    if head['has_medium']:
        GPIO.setup(head['medium'], GPIO.OUT)

for tally in tallies:
    GPIO.setup(tally['pgm'], GPIO.OUT)
    GPIO.setup(tally['pvw'], GPIO.OUT)


# Unitary features
def stop(head_ID):
    GPIO.output(heads[head_ID]['left'], GPIO.HIGH)
    GPIO.output(heads[head_ID]['right'], GPIO.HIGH)
    GPIO.output(heads[head_ID]['up'], GPIO.HIGH)
    GPIO.output(heads[head_ID]['down'], GPIO.HIGH)

def go_left(head_ID):
    GPIO.output(heads[head_ID]['left'], GPIO.LOW)
    GPIO.output(heads[head_ID]['right'], GPIO.HIGH)

def go_right(head_ID):
    GPIO.output(heads[head_ID]['left'], GPIO.HIGH)
    GPIO.output(heads[head_ID]['right'], GPIO.LOW)

def pan_stop(head_ID):
    GPIO.output(heads[head_ID]['left'], GPIO.HIGH)
    GPIO.output(heads[head_ID]['right'], GPIO.HIGH)

def go_up(head_ID):
    GPIO.output(heads[head_ID]['up'], GPIO.LOW)
    GPIO.output(heads[head_ID]['down'], GPIO.HIGH)

def go_down(head_ID):
    GPIO.output(heads[head_ID]['up'], GPIO.HIGH)
    GPIO.output(heads[head_ID]['down'], GPIO.LOW)

def tilt_stop(head_ID):
    GPIO.output(heads[head_ID]['up'], GPIO.HIGH)
    GPIO.output(heads[head_ID]['down'], GPIO.HIGH)

def move(head_ID, direction):
    heads[head_ID]['dir_pictures'] = default_dir_pictures.copy()
    if direction == 'stop':
        stop(head_ID)
        heads[head_ID]['dir_pictures'][4] = 'stop'
        heads[head_ID]['current_dir'] = direction
    elif direction == 'up':
        go_up(head_ID)
        pan_stop(head_ID)
        heads[head_ID]['dir_pictures'][1] = 'up'
        heads[head_ID]['current_dir'] = direction
    elif direction == 'down':
        go_down(head_ID)
        pan_stop(head_ID)
        heads[head_ID]['dir_pictures'][7] = 'down'
        heads[head_ID]['current_dir'] = direction
    elif direction == 'left':
        go_left(head_ID)
        tilt_stop(head_ID)
        heads[head_ID]['dir_pictures'][3] = 'left'
        heads[head_ID]['current_dir'] = direction
    elif direction == 'right':
        go_right(head_ID)
        tilt_stop(head_ID)
        heads[head_ID]['dir_pictures'][5] = 'right'
        heads[head_ID]['current_dir'] = direction
    elif direction == 'left_up':
        go_left(head_ID)
        go_up(head_ID)
        heads[head_ID]['dir_pictures'][0] = 'left_up'
        heads[head_ID]['current_dir'] = direction
    elif direction == 'left_down':
        go_left(head_ID)
        go_down(head_ID)
        heads[head_ID]['dir_pictures'][6] = 'left_down'
        heads[head_ID]['current_dir'] = direction
    elif direction == 'right_up':
        go_right(head_ID)
        go_up(head_ID)
        heads[head_ID]['dir_pictures'][2] = 'right_up'
        heads[head_ID]['current_dir'] = direction
    elif direction == 'right_down':
        go_right(head_ID)
        go_down(head_ID)
        heads[head_ID]['dir_pictures'][8] = 'right_down'
        heads[head_ID]['current_dir'] = direction

def low_speed(head_ID):
    GPIO.output(heads[head_ID]['slow'], GPIO.LOW)
    if heads[head_ID]['has_medium']:
        GPIO.output(heads[head_ID]['medium'], GPIO.HIGH)

def medium_speed(head_ID):
    GPIO.output(heads[head_ID]['slow'], GPIO.HIGH)
    if heads[head_ID]['medium']:
        GPIO.output(heads[head_ID]['medium'], GPIO.LOW)

def high_speed(head_ID):
    GPIO.output(heads[head_ID]['slow'], GPIO.HIGH)
    if heads[head_ID]['has_medium']:
        GPIO.output(heads[head_ID]['medium'], GPIO.HIGH)

def set_speed(head_ID, speed_setting):
    """
    Sets speed of MHP100 head. In case of wrong argument, no change is done.
    :param head_ID: ID of the head to be updated
    :param speed_setting: string with values slow, medium or fast
    :return: nothing
    """
    heads[head_ID]['speed_pictures'] = default_speed_pictures.copy()
    if speed_setting == 'slow':
        low_speed(head_ID)
        heads[head_ID]['speed_pictures'][0] = 'slow'
        heads[head_ID]['current_speed'] = speed_setting
    elif speed_setting == 'medium' and heads[head_ID]['has_medium']:
        medium_speed(head_ID)
        heads[head_ID]['speed_pictures'][1] = 'medium'
        heads[head_ID]['current_speed'] = speed_setting
    elif speed_setting == 'fast':
        high_speed(head_ID)
        heads[head_ID]['speed_pictures'][2] = 'fast'
        heads[head_ID]['current_speed'] = speed_setting


def set_tally(tally_ID, status):
    # Set the tally physical output according to request
    if status == 'pgm':
        GPIO.output(tallies[tally_ID]['pgm'], GPIO.HIGH)
        GPIO.output(tallies[tally_ID]['pvw'], GPIO.LOW)
        tallies[tally_ID]['current_status'] = 'PGM'
    elif status == 'pvw':
        GPIO.output(tallies[tally_ID]['pgm'], GPIO.LOW)
        GPIO.output(tallies[tally_ID]['pvw'], GPIO.HIGH)
        tallies[tally_ID]['current_status'] = 'PVW'
    else:
        status = 'off'
        GPIO.output(tallies[tally_ID]['pgm'], GPIO.LOW)
        GPIO.output(tallies[tally_ID]['pvw'], GPIO.LOW)
        tallies[tally_ID]['current_status'] = 'OFF'
    return status


def auto_test():
    """
    Move all heads in the 4 directions to make sure connectivity is OK
    :return: Nothing
    """
    nb_heads = len(heads)
    nb_tallies = len(tallies)

    print('go right')
    for tally_ID in range(nb_tallies):
        set_tally(tally_ID, 'pvw')
    for head_ID in range(nb_heads):
        go_right(head_ID)
    time.sleep(3)

    print('Go left')
    for tally_ID in range(nb_tallies):
        set_tally(tally_ID, 'pgm')
    for head_ID in range(nb_heads):
        go_left(head_ID)
    time.sleep(3)

    print('Pan Stop')
    for head_ID in range(nb_heads):
        pan_stop(head_ID)

    print('go up')
    for tally_ID in range(nb_tallies):
        set_tally(tally_ID, 'pvw')
    for head_ID in range(nb_heads):
        go_up(head_ID)
    time.sleep(3)

    print('Go down')
    for tally_ID in range(nb_tallies):
        set_tally(tally_ID, 'pgm')
    for head_ID in range(nb_heads):
        go_down(head_ID)
    time.sleep(2)

    print('tilt Stop')
    for tally_ID in range(nb_tallies):
        set_tally(tally_ID, 'off')
    for head_ID in range(nb_heads):
        tilt_stop(head_ID)


app = Flask(__name__)

@app.route('/mph', methods=['GET', 'POST'])
def home():
    # GET is used for a web page user interface
    if request.method == 'GET':
        if request.args.get('head_id'):
            head_id = int(request.args.get('head_id'))
        else:
            head_id = 0
        if head_id < len(heads):
            direction = request.args.get('move')
            if direction:
                move(head_id, direction)
            speed = request.args.get('speed')
            if speed:
                set_speed(head_id, speed)

        return render_template('mph_remote_tpl.html', heads=heads)

    # POST is used for a RESTful end point
    if request.method == 'POST':
        content = request.get_json()
        if 'head_id' in content:
            head_id = int(content['head_id'])
        else:
            head_id = 0
        if head_id < len(heads):
            if 'move' in content:
                move_requ = content['move'].lower()
                move(head_id, move_requ)
            if 'speed' in content:
                speed_req = content['speed']
                set_speed(head_id, speed_req)

            return jsonify({'head_id': head_id, 'move': heads[head_id]['current_dir'],
                            'speed': heads[head_id]['current_speed']})
        else:
            return jsonify({'error': 'invalid head ID'}), 400

    if request.user_agent:
        print(request.user_agent.platform)


@app.route('/favicon.ico')
def get_favicon():
    """
    Returns a favicon picture file to the web browser.
    This may not be visible, but it avoids and HTTP error if the web browser requests the favicon.
    :return: HTTP answser with icon file
    """
    return send_file('images/favicon.ico', mimetype='image/x-icon')


@app.route('/images/<img_filename>')
def get_image(img_filename):
    """
    Processes images files requests
    :param img_filename: the filename of the picture being requested
    :return: HTTP answer with picture file
    """
    return send_file('images/' + img_filename, mimetype='image/png')


@app.route('/tally', methods=['GET', 'POST'])
def tally():
    """
    Sets tally light to a given status
    :return: HTML page in case of get, JSON file in case of POST
    """
    if request.method == 'GET':
        if request.args.get('tally_id'):
            tally_id = int(request.args.get('tally_id'))
        else:
            tally_id = 0
        if tally_id < len(tallies) and request.args.get('status'):
            tally_status = request.args.get('status')
            set_tally(tally_id, tally_status)
        return render_template('tally_tpl.html', tallies=tallies)

    if request.method == 'POST':
        content = request.get_json()
        if 'tally_id' in content:
            tally_id = int(content['tally_id'])
        else:
            tally_id = 0
        if tally_id < len(tallies):
            if 'status' in content:
                tally_status = content['status'].lower()
                real_status = set_tally(tally_id, tally_status)
            else:
                real_status = set_tally(tally_id, 'off')
            return jsonify({'tally_id': tally_id, 'status': real_status})
        else:
            return jsonify({'tally_id': tally_id, 'status': 'unknown'}), 400


@app.route('/config', methods=['GET'])
def config():
    """
    Sets tally light to a given status
    :return: HTML page in case of get, JSON file in case of POST
    """
    if request.method == 'GET':
        config_response = build_config()

        return jsonify(config_response)


def build_config():
    config_heads = []
    for head in heads:
        config_heads = config_heads + [{
            'head_id': head['id'],
            'name': head['name'],
            'move': head['current_dir'],
            'speed': head['current_speed']}]
    if len(heads) > 0:
        config_response = {'heads': config_heads}
    else:
        config_response = {}
    config_tallies = []
    for tally in tallies:
        config_tallies = config_tallies + [{
            'tally_id': tally['id'],
            'name': tally['name'],
            'status': tally['current_status']}]
    if len(tallies) > 0:
        config_response = {'config': [config_response, {'tallies': config_tallies}]}
    return config_response


@app.route('/config/tally', methods=['POST'])
def config_tally():
    content = request.get_json()
    if 'tally_id' in content:
        tally_id = int(content['tally_id'])
    else:
        tally_id = 0
    if tally_id < len(tallies):
        if 'name' in content:
            tallies[tally_id]['name'] = content['name']
            hw_conf['tallies'][tally_id]['name'] = content['name']
            save_config(hw_conf)
            return jsonify(build_config())
        else:
            return jsonify(build_config()), 400
    else:
        return jsonify(build_config()), 400

@app.route('/config/head', methods=['POST'])
def config_head():
    content = request.get_json()
    if 'head_id' in content:
        head_id = int(content['head_id'])
    else:
        head_id = 0
    if head_id < len(heads):
        if 'name' in content:
            heads[head_id]['name'] = content['name']
            hw_conf['heads'][head_id]['name'] = content['name']
            save_config(hw_conf)
            return jsonify(build_config())
        else:
            return jsonify(build_config()), 400
    else:
        return jsonify(build_config()), 400


if __name__ == '__main__':

    auto_test()

    nb_heads = len(heads)
    for head_id in range(nb_heads):
        move(head_id, 'stop')
        set_speed(head_id, 'slow')

    app.run(host='0.0.0.0', port=int("80"))
