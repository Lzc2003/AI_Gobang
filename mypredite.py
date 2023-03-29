from ultralytics import YOLO    #YOLOV8
from PIL import Image
import cv2
import torch
import torchvision.transforms.functional as F
import numpy as np
import math
import serial                   #导入串口通信库
from time import sleep
import sys
import random
import pygame
from pygame.locals import *
import pygame.gfxdraw
from collections import namedtuple

#棋盘大小
chess_num=13
#初始化棋盘坐标13*13，初值为0，占用则变1
num_list = [ [0] * chess_num for i in range(chess_num)]
print(num_list)

#导入模型pt文件
model = YOLO("/home/zc/下载/ultralytics-main/runs/detect/train/weights/best.pt")

#初始化棋子
Chessman = namedtuple('Chessman', 'Name Value Color')
Point = namedtuple('Point', 'X Y')
BLACK_CHESSMAN = Chessman('黑子', 1, (45, 45, 45))
WHITE_CHESSMAN = Chessman('白子', 2, (219, 219, 219))

#棋子周围方向
offset = [(1, 0), (0, 1), (1, 1), (1, -1)]

#初始化串口
ser = serial.Serial()

#对串口的参数进行配置
def port_open_recv():
    ser.port='/dev/ttyUSB0'#端口号
    ser.baudrate=115200
    ser.bytesize=8
    ser.stopbits=1
    ser.parity='N'#奇偶校验位
    ser.open()
    if(ser.isOpen()):
        print("串口打开成功！")
    else:
        print("串口打开失败！")

#发送，注意编码格式
port_open_recv()
def send(send_data):
    if(ser.isOpen()):
        ser.write(send_data.encode('utf-8'))#编码
        print("发送成功",send_data)
    else:
        print("发送失败！")

##读取
# def recv(serial):
#     while True:
#         data = serial.read_all().decode('utf-8')  # str
#         if data == '':
#             continue
#         else:
#             break
#         sleep(0.02)
#     print(data)


#识别函数
def identify():
        #读图，将图片放进固定位置
        read_usb_capture()
        #推理
        results = model.predict(source="/home/zc/下载/ultralytics-main/guess/666.jpg", show=True,save=False,line_thickness=2,conf=0.2)
        #获得推理框坐标
        for result in results:
                boxes = result.boxes  # Boxes object for bbox outputs
                masks = result.masks  # Masks object for segmenation masks outputs
                probs = result.probs  # Class probabilities for classification outputs
                orig_shape=result.orig_shape
        i=boxes.__len__()
        for a in range(0,i):
                cm_x=(boxes.xyxy[a][0]+boxes.xyxy[a][2])/2
                cm_y=(boxes.xyxy[a][1]+boxes.xyxy[a][3])/2

                #相机坐标
                c=float(cm_x)
                d=float(cm_y)

                #转棋盘坐标参数，需通过test.py确定以下四个参数
                a_0=0.0273
                b_0=-11.94
                a_1=0.0266
                b_1=-3.57

                #棋盘坐标
                cm_x=int(round(c*a_0+b_0,0))
                cm_y=int(round(d*a_1+b_1,0))
                if num_list[cm_x][cm_y]==0 :
                        num_list[cm_x][cm_y]=1
                        # print(num_list[cm_x][cm_y])
                        return(cm_x,cm_y)
                        
                else:
                        continue

def read_usb_capture():
    # 选择摄像头的编号
    cap = cv2.VideoCapture(0)
    #分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    ## 添加这句是可以用鼠标拖动弹出的窗体
    #webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) 

    #三帧稳定后再取图
    flag=0
    cv2.namedWindow('real_img', cv2.WINDOW_NORMAL)
    while(cap.isOpened() and flag!=3):
        # 读取摄像头的画面
        ret, frame = cap.read()
        # 真实图
        cv2.imshow('real_img', frame)
        #图片放在固定位置，只推理图片，减少计算资源
        cv2.imwrite("/home/zc/下载/ultralytics-main/guess/" + str(666) + ".jpg", frame)
        flag=flag+1
        # 按下'q'就退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # 释放画面
    cap.release()
    cv2.destroyAllWindows()

#可视化棋盘
class Checkerboard:
    def __init__(self, line_points):
        self._line_points = line_points
        self._checkerboard = [[0] * line_points for _ in range(line_points)]

    def _get_checkerboard(self):
        return self._checkerboard

    checkerboard = property(_get_checkerboard)

    # 判断是否可落子
    def can_drop(self, point):
        return self._checkerboard[point.Y][point.X] == 0

    def drop(self, chessman, point):
        """
        落子
        :param chessman:
        :param point:落子位置
        :return:若该子落下之后即可获胜，则返回获胜方，否则返回 None
        """
        # 把黑棋/白棋落子的坐标打印出来
        print(f'{chessman.Name} ({point.X}, {point.Y})')
        print(num_list)
        if chessman.Name=='白子':
            ##print(point.X, point.Y)
            #串口内容
            str1=str(point.Y)+','+str(point.X)+'\r\n'
            print(str1)
            send(str1)
            #recv(ser).decode.encode('gbrk')#
            ##读取串口内容
            # data0=ser.read_all()#
        else:
            print("black")
            
        self._checkerboard[point.Y][point.X] = chessman.Value
        
        
        # 打印获胜方出来
        if self._win(point):
            print(f'{chessman.Name}获胜')
            return chessman

    # 判断是否赢了
    def _win(self, point):
        cur_value = self._checkerboard[point.Y][point.X]
        for os in offset:
            if self._get_count_on_direction(point, cur_value, os[0], os[1]):
                return True

    # 判断是否赢了的代码
    # 声明一个函数，按方向数数，数满5个就获胜。
    # 一个二维坐标上，判断上下、左右、两个45度直线，是否有五个相同的直连棋子，只要满足五颗子，则游戏结束:
    def _get_count_on_direction(self, point, value, x_offset, y_offset):
        count = 1
        for step in range(1, 5):
            x = point.X + step * x_offset
            y = point.Y + step * y_offset
            if 0 <= x < self._line_points and 0 <= y < self._line_points and self._checkerboard[y][x] == value:
                count += 1
            else:
                break
        for step in range(1, 5):
            x = point.X - step * x_offset
            y = point.Y - step * y_offset
            if 0 <= x < self._line_points and 0 <= y < self._line_points and self._checkerboard[y][x] == value:
                count += 1
            else:
                break

        return count >= 5
    
#可视化棋盘参数
SIZE = 30  # 棋盘每个点时间的间隔
Line_Points = chess_num  # 棋盘每行/每列点数
Outer_Width = 20  # 棋盘外宽度
Border_Width = 4  # 边框宽度
Inside_Width = 4  # 边框跟实际的棋盘之间的间隔
Border_Length = SIZE * (Line_Points - 1) + Inside_Width * 2 + Border_Width  # 边框线的长度
Start_X = Start_Y = Outer_Width + int(Border_Width / 2) + Inside_Width  # 网格线起点（左上角）坐标
SCREEN_HEIGHT = SIZE * (Line_Points - 1) + Outer_Width * 2 + Border_Width + Inside_Width * 2  # 游戏屏幕的高
SCREEN_WIDTH = SCREEN_HEIGHT + 200  # 屏幕的宽

Stone_Radius = SIZE // 2 - 3  # 棋子半径
Stone_Radius2 = SIZE // 2 + 3
Checkerboard_Color = (0xE3, 0x92, 0x65)  # 棋盘颜色
BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (255, 255, 255)
RED_COLOR = (200, 30, 30)
BLUE_COLOR = (30, 30, 200)
RIGHT_INFO_POS_X = SCREEN_HEIGHT + Stone_Radius2 * 2 + 10

def print_text(screen, font, x, y, text, fcolor=(255, 255, 255)):
    imgText = font.render(text, True, fcolor)
    screen.blit(imgText, (x, y))

def main():
    pygame.init()
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('五子棋')

    font1 = pygame.font.SysFont('SimHei', 32)  # 字体：黑体，32号
    font2 = pygame.font.SysFont('SimHei', 72)  # 字体：黑体，72号
    fwidth, fheight = font2.size('黑方获胜')

    checkerboard = Checkerboard(Line_Points)
    cur_runner = BLACK_CHESSMAN
    winner = None
    computer = AI(Line_Points, WHITE_CHESSMAN)

    # 设置黑白双方初始连子为0
    black_win_count = 0
    white_win_count = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    if winner is not None:
                        winner = None
                        cur_runner = BLACK_CHESSMAN
                        checkerboard = Checkerboard(Line_Points)
                        computer = AI(Line_Points, WHITE_CHESSMAN)
            else: 
                if winner is None:  # 检测是否有一方胜出
                    pressed_array = pygame.mouse.get_pressed()                       
                    (x,y)=identify()                       
                    click_point = Point(x,y)
                    print(click_point)
                    if checkerboard.can_drop(click_point):
                        winner = checkerboard.drop(cur_runner, click_point)
                        if winner is None:  # 再次判断是否有胜出
                            # 一个循环内检测两次，意思就是人出一次检测一下，电脑出一次检测一下。
                            cur_runner = _get_next(cur_runner)
                            computer.get_opponent_drop(click_point)
                            AI_point = computer.AI_drop()
                            winner = checkerboard.drop(cur_runner, AI_point)
                            del x,y
                            if winner is not None:
                                white_win_count += 1
                            cur_runner = _get_next(cur_runner)
                        else:
                            black_win_count += 1
                else:
                    print('超出棋盘区域')

        
        # 画棋盘
        _draw_checkerboard(screen)

        # 画棋盘上已有的棋子
        for i, row in enumerate(checkerboard.checkerboard):
            for j, cell in enumerate(row):
                if cell == BLACK_CHESSMAN.Value:
                    _draw_chessman(screen, Point(j, i), BLACK_CHESSMAN.Color)
                elif cell == WHITE_CHESSMAN.Value:
                    _draw_chessman(screen, Point(j, i), WHITE_CHESSMAN.Color)

        _draw_left_info(screen, font1, cur_runner, black_win_count, white_win_count)

        if winner:
            print_text(screen, font2, (SCREEN_WIDTH - fwidth) // 2, (SCREEN_HEIGHT - fheight) // 2, winner.Name + '获胜',
                       RED_COLOR)

        pygame.display.flip()


def _get_next(cur_runner):
    if cur_runner == BLACK_CHESSMAN:
        return WHITE_CHESSMAN
    else:
        return BLACK_CHESSMAN
    
# 画棋盘
def _draw_checkerboard(screen):
    # 填充棋盘背景色
    screen.fill(Checkerboard_Color)
    # 画棋盘网格线外的边框
    pygame.draw.rect(screen, BLACK_COLOR, (Outer_Width, Outer_Width, Border_Length, Border_Length), Border_Width)
    # 画网格线
    for i in range(Line_Points):
        pygame.draw.line(screen, BLACK_COLOR,
                         (Start_Y, Start_Y + SIZE * i),
                         (Start_Y + SIZE * (Line_Points - 1), Start_Y + SIZE * i),
                         1)
    for j in range(Line_Points):
        pygame.draw.line(screen, BLACK_COLOR,
                         (Start_X + SIZE * j, Start_X),
                         (Start_X + SIZE * j, Start_X + SIZE * (Line_Points - 1)),
                         1)
    # 画星位和天元
    for i in (3, 9, 15):
        for j in (3, 9, 15):
            if i == j == 9:
                radius = 5
            else:
                radius = 3
            # pygame.draw.circle(screen, BLACK, (Start_X + SIZE * i, Start_Y + SIZE * j), radius)
            pygame.gfxdraw.aacircle(screen, Start_X + SIZE * i, Start_Y + SIZE * j, radius, BLACK_COLOR)
            pygame.gfxdraw.filled_circle(screen, Start_X + SIZE * i, Start_Y + SIZE * j, radius, BLACK_COLOR)


# 画棋子
def _draw_chessman(screen, point, stone_color):
    # pygame.draw.circle(screen, stone_color, (Start_X + SIZE * point.X, Start_Y + SIZE * point.Y), Stone_Radius)
    pygame.gfxdraw.aacircle(screen, Start_X + SIZE * point.X, Start_Y + SIZE * point.Y, Stone_Radius, stone_color)
    pygame.gfxdraw.filled_circle(screen, Start_X + SIZE * point.X, Start_Y + SIZE * point.Y, Stone_Radius, stone_color)


# 画右侧信息显示
def _draw_left_info(screen, font, cur_runner, black_win_count, white_win_count):
    _draw_chessman_pos(screen, (SCREEN_HEIGHT + Stone_Radius2, Start_X + Stone_Radius2), BLACK_CHESSMAN.Color)
    _draw_chessman_pos(screen, (SCREEN_HEIGHT + Stone_Radius2, Start_X + Stone_Radius2 * 4), WHITE_CHESSMAN.Color)

    print_text(screen, font, RIGHT_INFO_POS_X, Start_X + 3, '玩家', BLUE_COLOR)
    print_text(screen, font, RIGHT_INFO_POS_X, Start_X + Stone_Radius2 * 3 + 3, '电脑', BLUE_COLOR)

    print_text(screen, font, SCREEN_HEIGHT, SCREEN_HEIGHT - Stone_Radius2 * 8, '战况：', BLUE_COLOR)
    _draw_chessman_pos(screen, (SCREEN_HEIGHT + Stone_Radius2, SCREEN_HEIGHT - int(Stone_Radius2 * 4.5)),
                       BLACK_CHESSMAN.Color)
    _draw_chessman_pos(screen, (SCREEN_HEIGHT + Stone_Radius2, SCREEN_HEIGHT - Stone_Radius2 * 2), WHITE_CHESSMAN.Color)
    print_text(screen, font, RIGHT_INFO_POS_X, SCREEN_HEIGHT - int(Stone_Radius2 * 5.5) + 3, f'{black_win_count} 胜',
               BLUE_COLOR)
    print_text(screen, font, RIGHT_INFO_POS_X, SCREEN_HEIGHT - Stone_Radius2 * 3 + 3, f'{white_win_count} 胜',
               BLUE_COLOR)


def _draw_chessman_pos(screen, pos, stone_color):
    pygame.gfxdraw.aacircle(screen, pos[0], pos[1], Stone_Radius2, stone_color)
    pygame.gfxdraw.filled_circle(screen, pos[0], pos[1], Stone_Radius2, stone_color)
    

class AI:
    def __init__(self, line_points, chessman):
        self._line_points = line_points
        self._my = chessman
        self._opponent = BLACK_CHESSMAN if chessman == WHITE_CHESSMAN else WHITE_CHESSMAN
        self._checkerboard = [[0] * line_points for _ in range(line_points)]

    def get_opponent_drop(self, point):
        self._checkerboard[point.Y][point.X] = self._opponent.Value

    def AI_drop(self):
        point = None
        score = 0
        for i in range(self._line_points):
            for j in range(self._line_points):
                if self._checkerboard[j][i] == 0:
                    _score = self._get_point_score(Point(i, j))
                    if _score > score:
                        score = _score
                        point = Point(i, j)
                    elif _score == score and _score > 0:
                        r = random.randint(0, 100)
                        if r % 2 == 0:
                            point = Point(i, j)
        self._checkerboard[point.Y][point.X] = self._my.Value
        return point

    def _get_point_score(self, point):
        score = 0
        for os in offset:
            score += self._get_direction_score(point, os[0], os[1])
        return score

    def _get_direction_score(self, point, x_offset, y_offset):
        count = 0  # 落子处我方连续子数
        _count = 0  # 落子处对方连续子数
        space = None  # 我方连续子中有无空格
        _space = None  # 对方连续子中有无空格
        both = 0  # 我方连续子两端有无阻挡
        _both = 0  # 对方连续子两端有无阻挡

        # 如果是 1 表示是边上是我方子，2 表示敌方子
        flag = self._get_stone_color(point, x_offset, y_offset, True)
        if flag != 0:
            for step in range(1, 6):
                x = point.X + step * x_offset
                y = point.Y + step * y_offset
                if 0 <= x < self._line_points and 0 <= y < self._line_points:
                    if flag == 1:
                        if self._checkerboard[y][x] == self._my.Value:
                            count += 1
                            if space is False:
                                space = True
                        elif self._checkerboard[y][x] == self._opponent.Value:
                            _both += 1
                            break
                        else:
                            if space is None:
                                space = False
                            else:
                                break  # 遇到第二个空格退出
                    elif flag == 2:
                        if self._checkerboard[y][x] == self._my.Value:
                            _both += 1
                            break
                        elif self._checkerboard[y][x] == self._opponent.Value:
                            _count += 1
                            if _space is False:
                                _space = True
                        else:
                            if _space is None:
                                _space = False
                            else:
                                break
                else:
                    # 遇到边也就是阻挡
                    if flag == 1:
                        both += 1
                    elif flag == 2:
                        _both += 1

        if space is False:
            space = None
        if _space is False:
            _space = None

        _flag = self._get_stone_color(point, -x_offset, -y_offset, True)
        if _flag != 0:
            for step in range(1, 6):
                x = point.X - step * x_offset
                y = point.Y - step * y_offset
                if 0 <= x < self._line_points and 0 <= y < self._line_points:
                    if _flag == 1:
                        if self._checkerboard[y][x] == self._my.Value:
                            count += 1
                            if space is False:
                                space = True
                        elif self._checkerboard[y][x] == self._opponent.Value:
                            _both += 1
                            break
                        else:
                            if space is None:
                                space = False
                            else:
                                break  # 遇到第二个空格退出
                    elif _flag == 2:
                        if self._checkerboard[y][x] == self._my.Value:
                            _both += 1
                            break
                        elif self._checkerboard[y][x] == self._opponent.Value:
                            _count += 1
                            if _space is False:
                                _space = True
                        else:
                            if _space is None:
                                _space = False
                            else:
                                break
                else:
                    # 遇到边也就是阻挡
                    if _flag == 1:
                        both += 1
                    elif _flag == 2:
                        _both += 1

        # 下面这一串score（分数）的含义：评估棋格获胜分数。
        # 能确定能让自己的棋子最有可能达成联机的位置，也就是最佳进攻位置，同理，计算机能计算出玩家的最大分值位置，并抢先玩家获得该位置，这样计算机就具有了防御的能力。
        # 在下棋之前，会计算空白棋格上的获胜分数，根据分数高低获取最佳位置。
        # 当已放置4颗棋子时，必须在第五个空棋格上设置绝对高的分值。
        # 当获胜组合上有部分位置已被对手的棋格占据而无法连成五子时，获胜组合上空棋格的获胜分数会直接设置为0。（四颗棋子，你把中间断了）
        # 当有两组及其以上的获胜组合位置交叉时，对该位置的分数进行叠加，形成分数比周围位置明显高。（五子棋中三三相连）

        score = 0
        if count == 4:
            score = 10000
        elif _count == 4:
            score = 9000
        elif count == 3:
            if both == 0:
                score = 1000
            elif both == 1:
                score = 100
            else:
                score = 0
        elif _count == 3:
            if _both == 0:
                score = 900
            elif _both == 1:
                score = 90
            else:
                score = 0
        elif count == 2:
            if both == 0:
                score = 100
            elif both == 1:
                score = 10
            else:
                score = 0
        elif _count == 2:
            if _both == 0:
                score = 90
            elif _both == 1:
                score = 9
            else:
                score = 0
        elif count == 1:
            score = 10
        elif _count == 1:
            score = 9
        else:
            score = 0

        if space or _space:
            score /= 2

        return score

    # 判断指定位置处在指定方向上是我方子、对方子、空
    def _get_stone_color(self, point, x_offset, y_offset, next):
        x = point.X + x_offset
        y = point.Y + y_offset
        if 0 <= x < self._line_points and 0 <= y < self._line_points:
            if self._checkerboard[y][x] == self._my.Value:
                return 1
            elif self._checkerboard[y][x] == self._opponent.Value:
                return 2
            else:
                if next:
                    return self._get_stone_color(Point(x, y), x_offset, y_offset, False)
                else:
                    return 0
        else:
            return 0
if __name__ == '__main__':
    main()    