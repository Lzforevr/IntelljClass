from ui.main_window import MainWindow
from detection.yolo_detector import YOLODetector
from detection.image_processor import ImageProcessor
from utils.data_processor import DataProcessor, HeatmapProcessor
import cv2
import time
from config import MODEL_PATH

class MainController:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.app = MainWindow()
        self.imgSize = self.app.getImgSize()
        self.yoloDetector = YOLODetector(MODEL_PATH)
        self.imageProcessor = ImageProcessor(self.imgSize)
        self.dataProcessor = DataProcessor()
        self.heatmapProcessor = HeatmapProcessor(self.imgSize)
        self.startTime = time.time()
        self._bind_export()
        self._start_detection()

    def _start_detection(self):
        def real_time_detection():
            ret, frame = self.cap.read()
            if ret:
                faceRects, faceCount = self.yoloDetector.detectFaces(frame)
                annotatedFrame = self.yoloDetector.get_annotated_frame(frame)
                frameResized, greyResized = self.imageProcessor.getResizedFrame(frame)
                resizedFaceRects, _ = self.yoloDetector.detectFaces(frameResized)
                heatmapRects = [(rect[0], rect[1], rect[2], rect[3]) for rect in resizedFaceRects]
                heatmap = self.heatmapProcessor.updateHeatmap(heatmapRects)
                imgTk = self.imageProcessor.processFrame(annotatedFrame, heatmap)
                self.app.displayFrame.image_label.configure(image=imgTk)
                self.app.displayFrame.image_label.image = imgTk
                try:
                    total = int(self.app.inputFrame.total_entry.get())
                    threshold = float(self.app.inputFrame.threshold_entry.get())
                    classStats = self.yoloDetector.get_class_stats()
                    headUpCount = 0
                    headDownCount = faceCount
                    lyingCount = 0
                    handCount = 0
                    personCount = 0
                    if classStats:
                        for stat in classStats:
                            if stat['class'] == 'Person':
                                personCount = stat['count']
                            elif stat['class'] == 'Head Up':
                                headUpCount = stat['count']
                            elif stat['class'] == 'Head Down':
                                headDownCount = stat['count']
                            elif stat['class'] == 'Lying':
                                lyingCount = stat['count']
                            elif stat['class'] == 'Raise Hand':
                                handCount = stat['count']
                    if total > 0:
                        if personCount > 0:
                            headUpRate = (headUpCount / total) * 100
                        else:
                            headUpRate = 0
                        handUpRate = (handCount / total) * 100 if total > 0 else 0
                        headDownLyingRate = ((headDownCount + lyingCount) / total) * 100 if total > 0 else 0
                        currentTime = time.time() - self.startTime
                        self.dataProcessor.updateData(currentTime, headUpRate, personCount,headUpCount, headDownCount, lyingCount, handCount)
                        statusText = f"实时抬头率：{headUpRate:.1f}%\n"
                        statusText += f"检测到的总人数：{personCount}\n"
                        statusText += f"抬头人数：{headUpCount}\n"
                        statusText += f"低头人数：{headDownCount}\n"
                        statusText += f"趴着人数：{lyingCount}\n"
                        statusText += f"举手人数：{handCount}\n"
                        statusText += f"设定总人数：{total}"
                        personStat = None
                        headUpStat = None
                        headDownStat = None
                        lyingStat = None
                        handStat = None
                        warningText = None
                        if classStats:
                            for stat in classStats:
                                if stat['class'] == 'Person':
                                    personStat = f"{stat['count']}个 (置信度: {stat['avg_confidence']})"
                                elif stat['class'] == 'Head Up':
                                    headUpStat = f"{stat['count']}个"
                                elif stat['class'] == 'Head Down':
                                    headDownStat = f"{stat['count']}个"
                                elif stat['class'] == 'Lying':
                                    lyingStat = f"{stat['count']}个"
                                elif stat['class'] == 'Raise Hand':
                                    handStat = f"{stat['count']}个"
                        if headUpRate < threshold:
                            warningText = "⚠️ 警告：当前抬头率低于设定阈值！"
                            self.app.statsFrame.frame.configure(style='Warning.TLabelframe')
                        else:
                            self.app.statsFrame.frame.configure(style='TLabelframe')
                        isLowHeadOrLying = headDownCount > 0 or lyingCount > 0
                        self.app.statsFrame.update_stats(statusText, personStat, headUpStat, headDownStat, lyingStat, handStat, warningText, is_low_head_or_lying=isLowHeadOrLying)
                        self.app.trendFrame.update_bars(headUpRate, handUpRate, headDownLyingRate)
                except ValueError:
                    self.app.statsFrame.var.set("请输入有效的总人数")
            self.app.window.after(100, real_time_detection)
        real_time_detection()

    def _bind_export(self):
        def export_data_callback():
            try:
                total = int(self.app.inputFrame.total_entry.get())
                self.dataProcessor.exportData(total, self.app.statsFrame.var)
                self.yoloDetector.reset_stats()
            except ValueError:
                self.app.statsFrame.var.set(self.app.statsFrame.var.get() + "\n\n⚠️ 请输入有效的总人数")
        self.app.exportFrame.export_button.configure(command=export_data_callback)

    def run(self):
        self.app.run()
        self.cap.release()
