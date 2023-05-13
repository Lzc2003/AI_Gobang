#!/usr/bin/env python

import rospy
import serial
import sys
import select
import termios
import tty

# 定义串口对象
ser = serial.Serial('/dev/ttyUSB0', 115200)

# 定义ROS节点
rospy.init_node('serial_keyboard', anonymous=True)

# 阻塞式读取
def getKey():
    tty.setraw(sys.stdin.fileno())
    select.select([sys.stdin], [], [], 0)
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

# 定义初始输入设置
settings = termios.tcgetattr(sys.stdin)

# 设置速度参数
linear_speed = 0.0
angular_speed = 0.0

# 发送速度数据到串口
def send_speeds(linear_speed, angular_speed):
    speed_str = "{} {}".format(linear_speed, angular_speed)
    speed_str += '\n'
    ser.write(speed_str.encode())

try:
    while (1):
        # 读取键盘输入
        key = getKey()
        rospy.loginfo("Key pressed: {}".format(key))
        
        # 设置速度参数
        if key == 'w':
            linear_speed = 1.0
        elif key == 's':
            linear_speed = -1.0
        elif key == 'a':
            angular_speed = 1.0
        elif key == 'd':
            angular_speed = -1.0
        elif key == 'x':
            linear_speed = 0.0
            angular_speed = 0.0
        else:
            continue

        # 发送速度数据到串口
        send_speeds(linear_speed, angular_speed)
        rospy.loginfo("Speeds set: linear = %f, angular = %f", linear_speed, angular_speed)

except Exception as e:
    rospy.logerr(e)

finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
