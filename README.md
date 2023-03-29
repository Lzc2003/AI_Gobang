# Lzc

#### 介绍
**基于yolov8的棋子识别及五子棋算法**

#### 软件功能
为下棋机器人提供识别功能以及策略




#### 使用说明

你需要关注的程序有：
                主要运行程序：mypredite.py
                训练参数配置程序：myfive.yaml
                训练程序：mytrain.py
                测试程序：，mytest.py            

在使用之前，请确保你正常安装yolov8相关配置，以下为相关链接

yolo8仓库：https://github.com/ultralytics/ultralytics

yolov8使用文档：https://docs.ultralytics.com/


如何制作自己的训练集：https://blog.csdn.net/sunchanglan151/article/details/116855746

####实现步骤：

    1.在five.yaml中配置相关参数：ultralytics-main/ultralytics/datasets/data/five.yaml
    2.在mytrain.py中配置相关参数：ultralytics-main/mytrain.py
    3.将获得的权重文件.pt文件替换mpredite.py中的pt文件
    4.在test.py中配置相关参数并解算获得相机坐标转世界坐标的参数
    5.修改mypredite.py的转换参数，并配置好相关摄像头接口，串口等参数即可使用


#### 参与贡献

2023.3.30Lzc提交代码


