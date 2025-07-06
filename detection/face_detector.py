import cv2
import numpy as np
from PIL import Image, ImageTk
from matplotlib import cm

class FaceDetector:
    def __init__(self, cascadePath):
        self.classifier = cv2.CascadeClassifier(cascadePath)
        
    def detectFaces(self, frame, scaleFactor=1.2, minNeighbors=3, minSize=(32, 32)):
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faceRects = self.classifier.detectMultiScale(grey, scaleFactor=scaleFactor,
                                                    minNeighbors=minNeighbors,
                                                    minSize=minSize)
        return faceRects, len(faceRects)

class ImageProcessor:
    def __init__(self, img_size):
        self.img_size = img_size
        
    def process_frame(self, frame, heatmap):
        # 调整帧大小
        frame_resized = cv2.resize(frame, (self.img_size, self.img_size))
        
        # 转换为RGB格式
        img = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        
        # 将热力图转换为彩色图像
        heatmap_color = (cm.jet(heatmap) * 255).astype(np.uint8)
        
        # 叠加热力图
        overlay = cv2.addWeighted(img, 1.0, heatmap_color[:,:,:3], 0.3, 0)
        
        # 转换为PIL图像
        img_pil = Image.fromarray(overlay)
        return ImageTk.PhotoImage(img_pil)
        
    def get_resized_frame(self, frame):
        frame_resized = cv2.resize(frame, (self.img_size, self.img_size))
        grey_resized = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
        return frame_resized, grey_resized