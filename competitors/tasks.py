from __future__ import absolute_import, unicode_literals

from celery import shared_task

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import serial
import time

@shared_task
def send_ready_task(pull_factor, weight):
    ser = serial.Serial(
        port='/dev/ttyUSB0',
        #port='/dev/pts/5',
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0.3
    )

    send_data = '>00pull_factor=' + str(pull_factor) + '%' + chr(13)
    ser.write(str.encode(send_data))
    time.sleep(0.3)

    send_data = '>00zero_load' + chr(13)
    ser.write(str.encode(send_data))
    time.sleep(0.3)

    send_data = '>00tractor_weight=' + str(weight) + 'kg' + chr(13)
    ser.write(str.encode(send_data))

    time.sleep(1)
    start_run_task()

@shared_task
def start_run_task():
    # start virtual serial ports pair - only for debug
    # socat -d -d pty,raw,echo=0 pty,raw,echo=0
    ser = serial.Serial(
        port='/dev/ttyUSB0',
        #port='/dev/pts/5',
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0.1
    )
    send_data = '>00start_run' + chr(13)
    ser.write(str.encode(send_data))
    delay = 0
    while True:
        x = ser.readline()
        delay += 1
        if delay < 1 and x.decode().find('stop') < 0:
            continue
        if not x:
            continue
        channel_layer = get_channel_layer()
        if x.decode().find('stop') >= 0:
            ser.write(str.encode('>00stop_run' + chr(13)))
            async_to_sync(channel_layer.group_send)(
                'room_rs232',
                {
                    'type': 'send_message',
                    'message': 'run finished',
                    'event': "END"
                }
            )
            break
        # ser.write(x)
        print(x)
        async_to_sync(channel_layer.group_send)(
            'room_rs232',
            {
                'type': 'send_message',
                'message': x.decode(),
                'event': "RS232"
            }
        )
        delay = 0

@shared_task
def send_msg_to_screen_task(msg):
    ser = serial.Serial(
        port='/dev/ttyUSB0',
        #port='/dev/pts/5',
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )
    send_data = '>00S' + msg + chr(13)
    ser.write(str.encode(send_data))
    print(send_data)