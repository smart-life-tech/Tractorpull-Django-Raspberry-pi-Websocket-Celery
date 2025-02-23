import time
import serial

ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate = 9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
)

distance = 0.00
time_ = 0.00
speed = 0.0
load = 0

# >run_distance =    0.04m
# >time =   0.00s
# >speed =  0.3kph
# >load =     0kg

cnt = 0

while 1:
        #send_data = '>00settings'+chr(13)
        send_data = '>run_distance =    '+str(round(distance, 2))+'m'
        ser.write(str.encode(send_data))
        print(send_data)

        send_data = '>time =   ' + str(round(time_, 2)) + 's'
        ser.write(str.encode(send_data))
        print(send_data)

        send_data = '>speed =  ' + str(round(speed, 2)) + 'kph'
        ser.write(str.encode(send_data))
        print(send_data)

        send_data = '>load =     ' + str(round(load, 2)) + 'kg'
        ser.write(str.encode(send_data))
        print(send_data)

        distance += 0.02
        time_ += 0.05
        speed += 0.1
        load += 1
        time.sleep(0.15)

        cnt += 1
        if cnt > 100:
                ser.write(str.encode('>stopped'))
                break