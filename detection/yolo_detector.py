import cv2
import numpy as np
from PIL import Image, ImageTk
from matplotlib import cm
from ultralytics import YOLO

class YOLODetector:
    def __init__(self, modelPath):
        self.model = YOLO(modelPath)
        # 更新为COCO数据集的17个关键点
        self.keypointNames = [
            'Nose', 'Left Eye', 'Right Eye', 'Left Ear', 'Right Ear',
            'Left Shoulder', 'Right Shoulder', 'Left Elbow', 'Right Elbow',
            'Left Wrist', 'Right Wrist', 'Left Hip', 'Right Hip',
            'Left Knee', 'Right Knee', 'Left Ankle', 'Right Ankle'
        ]
        self.keypointCounts = {i: 0 for i in range(len(self.keypointNames))}
        self.keypointConfSum = {i: 0.0 for i in range(len(self.keypointNames))}
        self.personCount = 0
        self.totalConfSum = 0.0
        
        # 添加动作统计
        self.actionNames = ['Head Down', 'Head Up', 'Lying', 'Raise Hand']
        self.actionCounts = {action: 0 for action in self.actionNames}
        
    def detectFaces(self, frame, confThreshold=0.5):
        # 使用YOLOv8-pose模型进行人体姿态检测
        results = self.model(frame, stream=True)
        
        # 处理结果
        faceRects = []
        headDownCount = 0
        
        # 重置本帧的统计信息
        self.personCount = 0
        self.actionCounts = {action: 0 for action in self.actionNames}
        
        for result in results:
            if hasattr(result, 'keypoints') and result.keypoints is not None:
                keypoints = result.keypoints.data
                boxes = result.boxes
                
                # 更新人数统计
                numPersons = len(boxes)
                self.personCount = numPersons
                
                for i, kpts in enumerate(keypoints):
                    # 获取边界框
                    if i < len(boxes):
                        box = boxes[i]
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        w, h = x2 - x1, y2 - y1
                        conf = float(box.conf)
                        self.totalConfSum += conf
                        
                        # 初始化动作状态
                        isHeadDown = False
                        isHeadUp = False
                        isStanding = False
                        isSitting = False
                        
                        if len(kpts) >= 17 and conf >= confThreshold:
                            # 获取关键点坐标
                            nose = kpts[0]  # 鼻子
                            left_eye = kpts[1]  # 左眼
                            right_eye = kpts[2]  # 右眼
                            left_ear = kpts[3]  # 左耳
                            right_ear = kpts[4]  # 右耳
                            left_shoulder = kpts[5]  # 左肩
                            right_shoulder = kpts[6]  # 右肩
                            left_elbow = kpts[7]  # 左肘
                            right_elbow = kpts[8]  # 右肘
                            left_knee = kpts[13]  # 左膝
                            right_knee = kpts[14]  # 右膝
                            face_keypoints = [nose, left_eye, right_eye]
                            visible_face_keypoints = sum(1 for kp in face_keypoints if kp[2] >= confThreshold)
                            # 方法1：通过鼻子和肩膀位置判断是否低头
                            
                            if nose[1] > left_shoulder[1] and nose[1] > right_shoulder[1]:
                                isHeadDown = True
                            else:
                                # 方法2：通过面部关键点可见性判断是否抬头
                                # 计算面部关键点的可见性（鼻子、眼睛、耳朵）
                                # 如果大部分面部关键点可见，则认为是抬头
                                if visible_face_keypoints == 3:
                                    isHeadUp = True
                                else:
                                    isHeadDown = True
                            
                            # 检测是否趴在桌子上（通过头部和肩部的位置关系判断）
                            # 如果头部位置明显低于肩部，且面部关键点不可见，则认为是趴着
                            is_lying = nose[1] > (left_shoulder[1] + right_shoulder[1])/2 + h * 0.2 and visible_face_keypoints <= 1
                            
                            # 检测是否举手（通过手腕和肘部的位置关系判断）
                            # 如果手腕位置高于肩部且靠近头部，则认为是在玩手机
                            left_wrist = kpts[9]  # 左手腕
                            right_wrist = kpts[10]  # 右手腕
                            is_raising_hand = (left_wrist[2] >= confThreshold and left_wrist[1] > left_elbow[1]) or \
                                            (right_wrist[2] >= confThreshold and right_wrist[1] > right_elbow[1])
                            
                            # 更新动作统计
                            if isHeadDown:
                                self.actionCounts['Head Down'] += 1
                                headDownCount += 1
                                faceRects.append((x1, y1, w, h, 'HEAD DOWN'))
                            elif isHeadUp:
                                self.actionCounts['Head Up'] += 1
                                faceRects.append((x1, y1, w, h, 'HEAD UP'))
                            
                            if is_lying:
                                self.actionCounts['Lying'] += 1
                            if is_raising_hand:
                                self.actionCounts['Raise Hand'] += 1
                        
                        # 更新关键点统计信息
                        for j, kpt in enumerate(kpts):
                            if j < len(self.keypointNames):
                                if kpt[2] >= confThreshold:  # 第三个值是置信度
                                    self.keypointCounts[j] += 1
                                    self.keypointConfSum[j] += float(kpt[2])
        
        return faceRects, headDownCount
    
    def get_annotated_frame(self, frame):
        # 使用YOLOv8-pose模型进行检测并绘制所有关键点和骨架
        results = self.model(frame, stream=True)
        
        for result in results:
            # 使用YOLOv8内置的绘图功能绘制所有检测结果
            annotated_frame = result.plot()
            
            # 添加动作标识
            if hasattr(result, 'keypoints') and result.keypoints is not None:
                keypoints = result.keypoints.data
                boxes = result.boxes
                
                for i, kpts in enumerate(keypoints):
                    if i < len(boxes):
                        box = boxes[i]
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        # 判断动作
                        action_text = self.determine_action(kpts)
                        
                        # 在边界框上方添加动作标识
                        cv2.putText(annotated_frame, action_text, (x1, y1 - 10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            return annotated_frame
        
        return frame  # 如果没有结果，返回原始帧
    
    def determine_action(self, keypoints, confThreshold=0.5):
        # 根据关键点判断动作
        if len(keypoints) < 17:
            return "Unknown"
        
        # 获取关键点
        nose = keypoints[0]
        left_eye = keypoints[1]
        right_eye = keypoints[2]
        left_ear = keypoints[3]
        right_ear = keypoints[4]
        left_shoulder = keypoints[5]
        right_shoulder = keypoints[6]
        left_elbow = keypoints[7]
        right_elbow = keypoints[8]
        left_knee = keypoints[13]
        right_knee = keypoints[14]
        
        # 计算面部关键点的可见性
        face_keypoints = [nose, left_eye, right_eye]
        visible_face_keypoints = sum(1 for kp in face_keypoints if kp[2] >= confThreshold)
        # 判断是否低头/抬头
        # 方法1：通过鼻子和肩膀位置判断是否低头
        
        if nose[1] > left_shoulder[1] and nose[1] > right_shoulder[1]:
            head_status = 'Head Up'
        else:
            # 方法2：通过面部关键点可见性判断是否抬头
            # 计算面部关键点的可见性（鼻子、眼睛、耳朵）
            # 如果大部分面部关键点可见，则认为是抬头
            if visible_face_keypoints == 3:
                head_status = 'Head Up'
            else:
                 head_status = 'Head Down'
        
        # 判断是否趴着/玩手机
        # 检测趴桌子状态
        is_lying = nose[1] > (left_shoulder[1] + right_shoulder[1])/2 + 30 and visible_face_keypoints <= 1
        
        # 检测玩手机状态
        left_wrist = keypoints[9]  # 左手腕
        right_wrist = keypoints[10]  # 右手腕
        is_raising_hand = (left_wrist[2] >= confThreshold and left_wrist[1] > left_elbow[1]) or \
                        (right_wrist[2] >= confThreshold and right_wrist[1] > right_elbow[1] )
        
        # 设置姿势状态
        posture = "LYING" if is_lying else ("RAISE HAND" if is_raising_hand else "")
        
        return f"{head_status}, {posture}"
    
    def get_class_stats(self):
        # 返回关键点和动作的统计信息
        stats = []
        
        # 添加人数统计
        if self.personCount > 0:
            avg_conf = self.totalConfSum / self.personCount
            stats.append({
                'class': 'Person',
                'count': self.personCount,
                'avg_confidence': f"{avg_conf:.3f}"
            })
        
        # 添加动作统计
        for action, count in self.actionCounts.items():
            if count > 0:
                stats.append({
                    'class': action,
                    'count': count,
                    'avg_confidence': 'N/A'
                })
        
        # 添加关键点统计
        for kpt_id in range(len(self.keypointNames)):
            if self.keypointCounts[kpt_id] > 0:
                avg_conf = self.keypointConfSum[kpt_id] / self.keypointCounts[kpt_id]
                stats.append({
                    'class': self.keypointNames[kpt_id],
                    'count': self.keypointCounts[kpt_id],
                    'avg_confidence': f"{avg_conf:.3f}"
                })
        
        return stats
    
    def reset_stats(self):
        # 重置统计信息
        self.keypointCounts = {i: 0 for i in range(len(self.keypointNames))}
        self.keypointConfSum = {i: 0.0 for i in range(len(self.keypointNames))}
        self.personCount = 0
        self.totalConfSum = 0.0
        self.actionCounts = {action: 0 for action in self.actionNames}

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