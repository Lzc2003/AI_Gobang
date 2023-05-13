#!/usr/bin/env python
import rospy
import serial
import struct
from geometry_msgs.msg import Twist

# 初始化串口
ser = serial.Serial('/dev/ttyUSB0', 115200)    # /dev/ttyUSB0为串口号，115200为波特率

def cmd_vel_callback(data):
    # 将浮点型线速度和角速度转换为整数类型
    linear_speed = int(data.linear.x * 1000)    # 将线速度转换为mm/s
    angular_speed = int(data.angular.z * 1000)  # 将角速度转换为deg/s

    # 将转换后的数据打包并发送到串口
    ser.write(struct.pack('>hh', linear_speed, angular_speed))

def main():
    # 初始化ROS节点
    rospy.init_node('cmd_vel_to_serial')
    # 订阅/cmd_vel话题并设置回调函数
    rospy.Subscriber('/cmd_vel', Twist, cmd_vel_callback)
    # 等待消息
    rospy.spin()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass