# coding: utf-8

import time
import json
import os.path
from flask import Flask, render_template, send_file, request, jsonify
import tally as ty
import head as hd

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

if 'heads' in hw_conf:
    heads = hd.init_heads(hw_conf['heads'])
    print(heads)
else:
    heads=[]

if 'tallies' in hw_conf:
    tallies = ty.init_tallies(hw_conf['tallies'])
    print(tallies)
else:
    tallies=[]


def auto_test():
    """
    Move all heads in the 4 directions to make sure connectivity is OK
    :return: Nothing
    """
    nb_heads = len(heads)
    nb_tallies = len(tallies)

    print('go right')
    for tally_ID in range(nb_tallies):
        ty.set_tally(tallies[tally_ID], 'pvw')
    for head_ID in range(nb_heads):
        hd.go_right(heads[head_ID])
    time.sleep(3)

    print('Go left')
    for tally_ID in range(nb_tallies):
        ty.set_tally(tallies[tally_ID], 'pgm')
    for head_ID in range(nb_heads):
        hd.go_left(heads[head_ID])
    time.sleep(3)

    print('Pan Stop')
    for head_ID in range(nb_heads):
        hd.pan_stop(heads[head_ID])

    print('go up')
    for tally_ID in range(nb_tallies):
        ty.set_tally(tallies[tally_ID], 'pvw')
    for head_ID in range(nb_heads):
        hd.go_up(heads[head_ID])
    time.sleep(3)

    print('Go down')
    for tally_ID in range(nb_tallies):
        ty.set_tally(tallies[tally_ID], 'pgm')
    for head_ID in range(nb_heads):
        hd.go_down(heads[head_ID])
    time.sleep(2)

    print('tilt Stop')
    for tally_ID in range(nb_tallies):
        ty.set_tally(tallies[tally_ID], 'off')
    for head_ID in range(nb_heads):
        hd.tilt_stop(heads[head_ID])


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
                hd.move(heads[head_id], direction)
            speed = request.args.get('speed')
            if speed:
                hd.set_speed(heads[head_id], speed)

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
                hd.move(heads[head_id], move_requ)
            if 'speed' in content:
                speed_req = content['speed']
                hd.set_speed(heads[head_id], speed_req)

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
            ty.set_tally(tallies[tally_id], tally_status)
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
                real_status = ty.set_tally(tallies[tally_id], tally_status)
            else:
                real_status = ty.set_tally(tallies[tally_id], 'off')
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
        hd.move(heads[head_id], 'stop')
        hd.set_speed(heads[head_id], 'slow')

    app.run(host='0.0.0.0', port=int("80"))
