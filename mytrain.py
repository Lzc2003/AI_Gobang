from ultralytics import YOLO

# Load a model
model = YOLO("yolov8n.yaml")  # build a new model from scratch
model = YOLO("yolov8n.pt")  # load a pretrained model (recommended for training)
# Train the model
model.train(data="/home/zc/下载/ultralytics-main/myfive.yaml", epochs=50, imgsz=1920,batch=6)