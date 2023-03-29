from ultralytics import YOLO
from PIL import Image
import cv2
matrix_X=[1]*13
matrix_Y=[1]*13

num1=[1]*13
num2=[1]*13
num3=[1]*13
num4=[1]*13
num5=[1]*13
num6=[1]*13
num7=[1]*13
num8=[1]*13
num9=[1]*13
num10=[1]*13
num11=[1]*13
num12=[1]*13
num0=[1]*13


# tis=[]
# for i in range(5):
#     tis.append([])
#     for j in range(5):
#         tis[i].append(j)
# print(tis)

# num_list[6][6]=1
# print(num_list)
model = YOLO("/home/zc/下载/ultralytics-main/runs/detect/train/weights/best.pt")
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
#     webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) 
    # 添加这句是可以用鼠标拖动弹出的窗体
flag=0
cv2.namedWindow('real_img', cv2.WINDOW_NORMAL)
while(cap.isOpened() and flag!=3):
        # 读取摄像头的画面
        ret, frame = cap.read()
        # 真实图
        cv2.imshow('real_img', frame)
        cv2.imwrite("/home/zc/下载/ultralytics-main/guess/" + str(666) + ".jpg", frame)
        flag=flag+1
        # 按下'q'就退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # 释放画面
cap.release()
cv2.destroyAllWindows()
results = model.predict(source="/home/zc/下载/ultralytics-main/guess/666.jpg", show=True,save=True,line_thickness=2,conf=0.2)
for result in results:
                boxes = result.boxes  # Boxes object for bbox outputs
                masks = result.masks  # Masks object for segmenation masks outputs
                probs = result.probs  # Class probabilities for classification outputs
                orig_shape=result.orig_shape
i=boxes.__len__()
for a in range(0,i):
                cm_x=(boxes.xyxy[a][0]+boxes.xyxy[a][2])/2
                cm_y=(boxes.xyxy[a][1]+boxes.xyxy[a][3])/2
                c=float(cm_x)
                d=float(cm_y)
                print(cm_x,cm_y)
                cm_x=int(round(c*0.0273-11.94,0))
                cm_y=int(round(d*0.0266-3.57,0))
                #print(cm_x,cm_y)
                print("棋面坐标为：",cm_x,cm_y)



        
        