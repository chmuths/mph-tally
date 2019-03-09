# mph-tally
This repo contains Python code and HTML templates for a Raspberry Pi based video motorized head and tally management.

Up to 3 motorized heads and 3 tally lights are supported.

Supported moving head is currently only MPH100
Tally is a PGM/PVW which can be output on a 3.5 mm jack like the datavideo ITC-100. As the Rasperry Pi outputs 3.3V on its pins, while tally devices usually require contact closure to ground, an optocoupler isolation is recommended. The Raspberry Pi can drive directly the optocoupler's LED, with a resistor for current limitation, and the transistor side will do the contact closure.

Hardware description is contained in a json file


## Interactive web interface

Two interactive web pages are provided. Port 80 is used for convenience. If you run this application manually, you need to use sudo. But it's much more convenient to run it at startup.
IP@/mph 
IP@/tally

## REST API

### GET /config
Returns a json describing the hardware configuration and names.
{
  "config": [
    {
      "heads": [
        {
          "head_id": 0, 
          "move": "stop", 
          "name": "CAM1", 
          "speed": "slow"
        }, 
        {
          "head_id": 1, 
          "move": "stop", 
          "name": "CAM 002", 
          "speed": "slow"
        }, 
        {
          "head_id": 2, 
          "move": "stop", 
          "name": "CAM3", 
          "speed": "slow"
        }
      ]
    }, 
    {
      "tallies": [
        {
          "name": "external", 
          "status": "PVW", 
          "tally_id": 0
        }, 
        {
          "name": "my bigger screen", 
          "status": "PGM", 
          "tally_id": 1
        }, 
        {
          "name": "right screen", 
          "status": "PVW", 
          "tally_id": 2
        }
      ]
    }
  ]
}

### POST /config/tally
allows to change the name of the tally output
json content to post like {'tally_id': 1, 'name': 'my little monitor'}
tally_id defaults to 0 if ommitted
Returns the description json 

### POST /config/mph
allows to change the name of the head (makes sense to put the CAM name)
json content to post like {'head_id': 1, 'name': 'CAM 002'}
head_id defaults to 0 if ommitted
Returns the description json

### POST /tally
Sets tally statys to PGM, PVW, OFF
json content to post like {'tally_id': 1, 'status': 'pgm'}

### POST /mph
Control speed and direction of head
json content to post like {'head_id': 2, 'speed': 'slow', 'move': 'right_up'}
Allowed values for speed : slow, medium, fast
Allowed values for move : stop, up, down left, right, left_up, left_down, right_up, right_down

