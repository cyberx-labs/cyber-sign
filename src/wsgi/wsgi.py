#!/usr/bin/env python
import sys
import os
import threading

sys.path.append(os.path.dirname(__file__))

import logging
import time
import re
import json
import serial
from serial.tools import list_ports
from wsgiref.simple_server import make_server

PORT = 8080

# --------------------------
# Serial interface init

try:

    ports = list(list_ports.comports())
    arduino = None

    # Let's assume that the only serial port connected to this raspberry pi -> arduino port
    for port_id, port_name, port_address in ports:
        arduino = serial.Serial(port_id, baudrate=9600)
        break

    if not arduino:
        raise Exception('Arduino not detected')

except:
    logging.exception('serial communication init with Arduino failed')
    raise

# --------------------------

_lock = threading.Lock()


def _set_color(color):
    with _lock:
        logging.info('applying {0} color'.format(color))

        # Write each character (won't work otherwise :\ wasted about an hour of debugging on this one)
        for c in color:
            arduino.write(c)
            time.sleep(0.1)

        arduino.flush()
        time.sleep(1)


_color = '000000'
_set_color(_color)


def _handle_request(method, url):
    global _color

    url = url.lower()
    url = url.strip().strip('/')

    if url.startswith('color'):
        m = re.search(r'color/([0-9a-f]{6})/?$', url, re.IGNORECASE)
        if m:
            _color = m.group(1).lower()
            _set_color(_color)

    return {"color": _color}


def application(environ, start_response):
    headers = [('Content-Type', 'application/json')]

    method = environ['REQUEST_METHOD']
    url = _get_url(environ)

    try:
        response = _handle_request(method, url)
        start_response('200 OK', headers)
        return json.dumps(response) if response else ''
    except Exception as ex:
        start_response('500 ERROR', headers)
        return json.dumps({"error": str(ex)})


def _get_url(environ):
    url = environ.get('PATH_INFO')
    if url:
        return url

    return environ.get('REQUEST_URI')


if __name__ == "__main__":
    httpd = make_server('0.0.0.0', PORT, application)
    print "Serving on port {0}...".format(PORT)
    httpd.serve_forever()
