#!/usr/bin/env python

import rospy
import serial
from std_msgs.msg import Float32

# 定义串口对象
ser = serial.Serial('/dev/ttyUSB0', 115200)

# 定义ROS节点
rospy.init_node('odometry_publisher', anonymous=True)

# 定义ros话题
pub = rospy.Publisher('odometry', Float32, queue_size=10)

while not rospy.is_shutdown():
    # 从串口读取数据
    data = ser.readline().decode('utf-8')
    # 将数据转换为Float32格式
    try:
        odom = Float32(float(data))
        # 发布数据到ROS话题
        pub.publish(odom)
        rospy.loginfo("Odometry data: %f", odom)
    # 处理数据转换异常
    except ValueError:
        rospy.logerr("Invalid data received from serial port: %s", data)