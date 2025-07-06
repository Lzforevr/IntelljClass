# 课堂抬头率监测系统

## 项目说明

本项目是一个基于计算机视觉的课堂抬头率监测系统，使用YOLO11n-pose模型检测学生的头部姿态，实时计算课堂抬头率，并提供数据可视化和导出功能。

## 主要功能

1. 实时摄像头画面采集
2. 基于YOLO11n-pose的姿态检测
3. 抬头率实时计算与显示
4. 抬头率趋势图可视化
5. 热力图显示
6. 数据导出功能

## 技术栈

- **深度学习框架**: PyTorch + Ultralytics YOLO11
- **计算机视觉**: OpenCV
- **界面开发**: Tkinter
- **数据处理**: NumPy, Pandas
- **数据可视化**: Matplotlib
- **图像处理**: PIL

## 项目结构

```
IntelliClass/
├── config.py              # 配置文件
├── controller.py           # 主控制器
├── main.py                # 程序入口
├── main.spec              # 打包配置
├── README.md              # 项目说明
├── detection/             # 检测模块
│   ├── face_detector.py   # 人脸检测器
│   ├── image_processor.py # 图像处理器
│   └── yolo_detector.py   # YOLO检测器
├── model/                 # 模型文件
│   └── yolo11n-pose.pt   # YOLO11n姿态检测模型
├── export_data/          # 导出数据目录
├── static/               # 静态资源
├── train/                # 训练相关
├── ui/                   # 用户界面
└── utils/                # 工具函数
```

## 安装与使用

### 环境要求

- Python 3.8+
- PyTorch
- OpenCV
- Ultralytics

### 安装依赖

```bash
pip install torch torchvision torchaudio
pip install ultralytics
pip install opencv-python
pip install numpy pandas matplotlib pillow
pip install tkinter
```

### 运行程序

```bash
python main.py
```

## 模型说明

本系统使用了YOLO11n-pose模型进行姿态检测，模型文件位于`model/yolo11n-pose.pt`。

YOLO11n-pose是一个轻量化的姿态检测模型，能够：
- 检测人体关键点
- 分析头部姿态
- 实时推理，适合实际应用场景

### 检测原理

系统通过分析人体关键点（特别是头部和肩部关键点）来判断学生的姿态：
- 计算头部相对于肩部的角度
- 判断是否处于"低头"状态
- 统计抬头率 = (总人数 - 低头人数) / 总人数

## 功能特性

### 1. 实时检测
- 支持摄像头实时画面采集
- 实时姿态检测和分析
- 低延迟显示

### 2. 数据统计
- 实时计算抬头率
- 抬头率趋势图显示
- 历史数据记录

### 3. 可视化
- 检测框和关键点标注
- 热力图显示人员分布
- 图表展示统计数据

### 4. 数据导出
- 支持CSV格式导出
- 包含时间戳和抬头率数据
- 便于后续分析

## 核心模块

### [`FaceDetector`](detection/face_detector.py)
负责人脸检测功能，使用OpenCV的Haar级联分类器：

```python
class FaceDetector:
    def __init__(self, cascadePath):
        self.classifier = cv2.CascadeClassifier(cascadePath)
    
    def detectFaces(self, frame, scaleFactor=1.2, minNeighbors=3, minSize=(32, 32)):
        # 人脸检测逻辑
```

### [`ImageProcessor`](detection/face_detector.py)
处理图像和热力图叠加：

```python
class ImageProcessor:
    def process_frame(self, frame, heatmap):
        # 图像处理和热力图叠加
```

### YOLO检测器
基于YOLO11n-pose模型的姿态检测模块，位于[`detection/yolo_detector.py`](detection/yolo_detector.py)。

## 配置说明

主要配置项在[`config.py`](config.py)中定义：
- 模型路径配置
- 检测参数调优
- 界面显示设置
- 数据导出路径

## 性能优化

1. **模型优化**: 使用轻量化的YOLO11n-pose模型
2. **推理加速**: 支持GPU加速推理
3. **内存管理**: 优化图像处理流程
4. **实时性**: 多线程处理确保界面流畅

## 应用场景

- 课堂教学质量监测
- 在线教育专注度分析
- 会议参与度统计
- 学习行为研究

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进项目。

