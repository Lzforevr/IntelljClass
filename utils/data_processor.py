import os
import csv
from datetime import datetime
import numpy as np
from collections import deque

class DataProcessor:
    def __init__(self, maxPoints=50):
        self.maxPoints = maxPoints
        self.timePoints = deque(maxlen=maxPoints)
        self.ratePoints = deque(maxlen=maxPoints)
        self.faceCount = 0
        self.headUpCount = 0
        self.headDownCount = 0
        self.lyingCount = 0
        self.handCount = 0
        
    def updateData(self, timePoint, rate, faceCount, headUpCount=0, headDownCount=0, lyingCount=0, handCount=0):
        self.timePoints.append(timePoint)
        self.ratePoints.append(rate)
        self.faceCount = faceCount
        self.headUpCount = headUpCount
        self.headDownCount = headDownCount
        self.lyingCount = lyingCount
        self.handCount = handCount

        
    def exportData(self, total, var):
        try:
            if len(self.timePoints) == 0:
                var.set(var.get() + "\n\n⚠️ 暂无数据可导出")
                return
                
            if total <= 0:
                var.set(var.get() + "\n\n⚠️ 请输入有效的总人数")
                return
                
            # 创建导出目录
            exportDir = 'export_data'
            if not os.path.exists(exportDir):
                os.makedirs(exportDir)
                
            # 生成文件名和完整路径
            filename = f'抬头率数据_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            filepath = os.path.join(exportDir, filename)
            
            # 写入数据
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['时间(秒)', '抬头率(%)', '检测到的人脸数','抬头人数', '低头人数','趴卧人数','举手人数', '总人数'])
                for t, r in zip(self.timePoints, self.ratePoints):
                    writer.writerow([f"{t:.1f}", f"{r:.1f}", self.faceCount,self.headUpCount,self.headDownCount,self.lyingCount,self.handCount, total])
                    
            var.set(var.get() + f"\n\n✅ 数据已导出至 {filepath}")
            
        except PermissionError:
            var.set(var.get() + "\n\n❌ 无法写入文件，请检查权限")
        except Exception as e:
            var.set(var.get() + f"\n\n❌ 导出失败：{str(e)}")

class HeatmapProcessor:
    def __init__(self, imgSize):
        self.imgSize = imgSize
        self.heatmap = np.zeros((imgSize, imgSize), dtype=np.float32)
        self.alpha = 0.3  # 热力图透明度
        self.decay = 0.9  # 热力图衰减率
        
    def updateHeatmap(self, faceRects):
        self.heatmap *= self.decay
        for (x, y, w, h) in faceRects:
            self.heatmap[y:y+h, x:x+w] += 0.1
            self.heatmap[self.heatmap > 1.0] = 1.0
        return self.heatmap