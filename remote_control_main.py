#!/usr/bin/python 
# coding: utf-8
import math
from flask import Flask, render_template
from flask_socketio import SocketIO

from pymouse import PyMouse
from pykeyboard import PyKeyboard

# import numpy as np
import logging
logging.basicConfig(level=logging.WARNING)
m = PyMouse()
k = PyKeyboard()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


def clip(x, min_v, max_v):
    if x < min_v:
        return min_v
    elif x > max_v:
        return max_v
    else:
        return x


@socketio.on('debug')
def handle_debug(message):
    print message


@socketio.on('change_language')
def handle_change_language(message):
    print ('change_language')
    k.press_keys([k.alt_l_key, k.shift_l_key])


@socketio.on('change_window')
def handle_change_window(message):
    print ('change_window')
    k.press_keys([k.alt_l_key, k.tab_key])


@socketio.on('keypress')
def handle_message(message):
    # print message
    hebrew_letters = u'קראטוןםפשדגכעיחלךףזסבהנמצתץ'
    english_letters = u'ertyuiopasdfghjkl;zxcvbnm,.'
    assert len(hebrew_letters) == len(english_letters)
    key_mapping = dict(zip(hebrew_letters, english_letters), **{13: k.return_key, 8: k.backspace_key, 32: k.space})
    try:
        if 'key' in message:
            key = message['key']
            if isinstance(key, basestring):
                k_out = ''
                for kk in key:
                    if kk in key_mapping:
                        k_out += key_mapping[kk]
                    else:
                        k_out += kk
                key = k_out
            elif key in key_mapping:
                key = key_mapping[key]

            if isinstance(key, int):
                k.tap_key(key)
            else:
                for kk in key:
                    k.tap_key(kk)
    # else:
    #         k.type_string(message['letter'])

    except Exception as e:
        print('ERROR')
        print(e)
        print(message)


@socketio.on('mouse')
def handle_mouse(message):
    # print message
    try:
        if 'top' in message:
            x_dim, y_dim = m.screen_size()
            x, y = message['left'], message['top']
            x, y = map(lambda x: clip(x, 0.0, 1.0), [x, y])
            x, y = int(x * x_dim), int(y * y_dim)
            m.move(x, y)
            if 'button' in message:
                m.click(x, y, button=message['button'])
                print message
        elif 'scroll' in message:
            m.scroll(message['scroll'])
            # k.tap_key(message['key'])
    # else:
    #         k.type_string(message['letter'])
    #
    except:
        print(message)


if __name__ == '__main__':
    import platform;

    port = 33333
    print 'connect to: http://%s:%d/static/mobile.html' % (platform.uname()[1], port)
    socketio.run(app, port=port, host='0.0.0.0')
