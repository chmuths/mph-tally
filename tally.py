# coding: utf-8

import RPi.GPIO as GPIO


def init_tallies(tally_config):

    tallies=[]
    tally_id = 0
    for tally in tally_config:
        tallies = tallies + [{'name': tally['name'],
                              'id': tally_id,
                              'pgm': tally['ports']['pgm'],
                              'pvw': tally['ports']['pvw'],
                              'logic': 'active_high',
                              'current_status': 'OFF'}]
        if 'logic' in tally['ports']:
            if tally['ports']['logic'] == 'active_low':
                tallies[tally_id]['logic'] = tally['ports']['logic']
        tally_id += 1

    print(tallies)

    # Set GPIO naming convention
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Initialize ports
    for tally in tallies:
        for port in tally['pgm']:
            GPIO.setup(port, GPIO.OUT)
        for port in tally['pvw']:
            GPIO.setup(port, GPIO.OUT)

    return tallies


def set_tally(tally, status):
    # Set the tally physical output according to request
    if status == 'pgm':
        if tally['logic'] == 'active_high':
            for port in tally['pvw']:
                GPIO.output(port, GPIO.LOW)
            for port in tally['pgm']:
                GPIO.output(port, GPIO.HIGH)
        else:
            for port in tally['pvw']:
                GPIO.output(port, GPIO.HIGH)
            for port in tally['pgm']:
                GPIO.output(port, GPIO.LOW)
        tally['current_status'] = 'PGM'
    elif status == 'pvw':
        if tally['logic'] == 'active_high':
            for port in tally['pgm']:
                GPIO.output(port, GPIO.LOW)
            for port in tally['pvw']:
                GPIO.output(port, GPIO.HIGH)
        else:
            for port in tally['pgm']:
                GPIO.output(port, GPIO.HIGH)
            for port in tally['pvw']:
                GPIO.output(port, GPIO.LOW)
        tally['current_status'] = 'PVW'
    else:
        status = 'off'
        if tally['logic'] == 'active_high':
            for port in tally['pgm']:
                GPIO.output(port, GPIO.LOW)
            for port in tally['pvw']:
                GPIO.output(port, GPIO.LOW)
        else:
            for port in tally['pgm']:
                GPIO.output(port, GPIO.HIGH)
            for port in tally['pvw']:
                GPIO.output(port, GPIO.HIGH)
        tally['current_status'] = 'OFF'
    return status


