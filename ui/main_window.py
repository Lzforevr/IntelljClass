import tkinter as tk
from tkinter import ttk
from tkinter import StringVar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm
from PIL import Image, ImageTk
try:
    resample_lanczos = Image.Resampling.LANCZOS
except AttributeError:
    resample_lanczos = Image.NEAREST

fontPath = 'ui/AlimamaShuHeiTi-Bold.ttf'
customFont = fm.FontProperties(fname=fontPath)

class MainWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('智瞳课堂——课堂活跃度实时监测系统')
        self.screenWidth = self.window.winfo_screenwidth()
        self.screenHeight = self.window.winfo_screenheight()
        self.windowWidth = int(self.screenWidth * 0.9)
        self.windowHeight = int(self.screenHeight * 0.9)
        self.baseFont = int(self.windowHeight * 0.035)
        self.imgSize = int(self.windowWidth * 0.6)
        self.window.geometry(f'{self.windowWidth}x{self.windowHeight}')
        try:
            self.borderImagePil = Image.open("static/border.png")
            self.borderImagePil = self.borderImagePil.resize((self.windowWidth, self.windowHeight), resample_lanczos)
            self.borderImage = ImageTk.PhotoImage(self.borderImagePil)
            self.backgroundLabel = tk.Label(self.window, image=self.borderImage)
            self.backgroundLabel.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading border image: {e}")
            self.window.configure(bg='#f5f5f7')
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False
        self._initStyles()
        self._createMainFrame()
        self._createFrames()

    def _initStyles(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')
        except:
            pass
        bgColor = '#f5f5f7'
        accentColor = '#007aff'
        textColor = '#333333'
        fontFamily = customFont.get_name()
        self.style.configure('TFrame', background=bgColor)
        self.style.configure('TLabel', background=bgColor, foreground=textColor, font=(fontFamily, self.baseFont))
        self.style.configure('TEntry', font=(fontFamily, self.baseFont))
        self.style.configure('TButton', font=(fontFamily, self.baseFont), background=accentColor)
        self.style.map('TButton', background=[('active', '#0069d9'), ('pressed', '#0062cc')])
        self.style.configure('TLabelframe', background=bgColor, font=(fontFamily, self.baseFont))
        self.style.configure('TLabelframe.Label', background=bgColor, foreground=textColor, font=(fontFamily, self.baseFont))
        warningBg = '#fff3cd'
        warningFg = '#856404'
        self.style.configure('Warning.TLabelframe', background=warningBg)
        self.style.configure('Warning.TLabelframe.Label', background=warningBg, foreground=warningFg, font=(fontFamily, self.baseFont))

    def _createMainFrame(self):
        self.mainFrame = ttk.Frame(self.window, padding="10")
        self.mainFrame.grid(row=0, column=0, sticky="nsew")
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.mainFrame.grid_columnconfigure(0, weight=1)
        self.mainFrame.grid_columnconfigure(1, weight=1)
        self.mainFrame.grid_rowconfigure(1, weight=3)
        self.mainFrame.grid_rowconfigure(2, weight=1)
        self.mainFrame.grid_rowconfigure(3, weight=2)

    def _createFrames(self):
        self.titleLabel = ttk.Label(self.mainFrame, text="课堂抬头率实时监测系统",
                                    font=(customFont.get_name(), int(self.baseFont * 1.5), 'bold'))
        self.titleLabel.grid(column=0, row=0, columnspan=2, pady=self.windowHeight//40)
        self.inputFrame = InputFrame(self.mainFrame, self.baseFont)
        self.inputFrame.frame.grid(column=0, row=1, padx=10, pady=5, sticky="nsew")
        self.displayFrame = DisplayFrame(self.mainFrame, self.imgSize, self.baseFont)
        self.displayFrame.frame.grid(column=1, row=1, padx=10, pady=5, sticky="nsew")
        self.statsFrame = StatsFrame(self.mainFrame, self.baseFont)
        self.statsFrame.frame.grid(column=0, row=2, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.trendFrame = PoseRatioFrame(self.mainFrame, self.windowWidth, self.windowHeight, self.baseFont)
        self.trendFrame.frame.grid(column=0, row=3, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.exportFrame = ExportFrame(self.mainFrame, self.baseFont)
        self.exportFrame.frame.grid(column=0, row=4, columnspan=2, padx=10, pady=5)

    def run(self):
        self.window.mainloop()

    def getImgSize(self):
        return self.imgSize

class InputFrame:
    def __init__(self, parent, base_font):
        # 加载图标
        try:
            self.icon_image_pil = Image.open("static/config_icon.png").resize((20, 20), resample_lanczos)
            self.icon_image = ImageTk.PhotoImage(self.icon_image_pil)
        except Exception as e:
            print(f"Error loading config_icon.png: {e}")
            self.icon_image = None

        # 创建标题的 Frame
        title_frame = tk.Frame(parent)
        if self.icon_image:
            icon_label = ttk.Label(title_frame, image=self.icon_image)
            icon_label.pack(side=tk.LEFT, padx=(0, 5))
        text_label = ttk.Label(title_frame, text=" 配置区域")
        text_label.pack(side=tk.LEFT)

        self.frame = ttk.LabelFrame(parent, labelwidget=title_frame, padding="10")
        self.frame.grid_columnconfigure(1, weight=1)
        
        # 定义自定义总人数输入框和标签
        self.total_label = ttk.Label(self.frame, text="课堂总人数：")
        self.total_label.grid(column=0, row=0, padx=5, pady=5, sticky='w')
        self.total_entry = ttk.Entry(self.frame, width=20)
        self.total_entry.grid(column=1, row=0, padx=5, pady=5)
        
        # 定义抬头率阈值输入框和标签
        self.threshold_label = ttk.Label(self.frame, text="抬头率阈值(%)：")
        self.threshold_label.grid(column=0, row=1, padx=5, pady=5, sticky='w')
        self.threshold_entry = ttk.Entry(self.frame, width=20)
        self.threshold_entry.insert(0, "60")  # 默认阈值60%
        self.threshold_entry.grid(column=1, row=1, padx=5, pady=5)

class DisplayFrame:
    def __init__(self, parent, img_size, base_font):
        # 加载图标
        try:
            self.icon_image_pil = Image.open("static/display_icon.png").resize((20, 20), resample_lanczos)
            self.icon_image = ImageTk.PhotoImage(self.icon_image_pil)
        except Exception as e:
            print(f"Error loading display_icon.png: {e}")
            self.icon_image = None

        # 创建标题的 Frame
        title_frame = tk.Frame(parent)
        if self.icon_image:
            icon_label = ttk.Label(title_frame, image=self.icon_image)
            icon_label.pack(side=tk.LEFT, padx=(0, 5))
        text_label = ttk.Label(title_frame, text=" 监测区域")
        text_label.pack(side=tk.LEFT)

        self.frame = ttk.LabelFrame(parent, labelwidget=title_frame, padding="10")
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)
        
        # 显示所选教室实时图像的标签
        self.pic_tip = ttk.Label(self.frame, text="实时摄像头画面", font=(customFont.get_name(), int(base_font * 0.8)))
        self.pic_tip.grid(column=0, row=0, pady=5)
        
        # 初始化图片显示
        self.image_label = ttk.Label(self.frame)
        self.image_label.grid(column=0, row=1, pady=5, padx=5, sticky="nsew")

class StatsFrame:
    def __init__(self, parent, base_font):
        # 加载图标
        try:
            self.icon_image_pil = Image.open("static/stats_icon.png").resize((20, 20), resample_lanczos)
            self.icon_image = ImageTk.PhotoImage(self.icon_image_pil)
        except Exception as e:
            print(f"Error loading stats_icon.png: {e}")
            self.icon_image = None

        # 创建标题的 Frame
        title_frame = tk.Frame(parent)
        if self.icon_image:
            icon_label = ttk.Label(title_frame, image=self.icon_image)
            icon_label.pack(side=tk.LEFT, padx=(0, 5))
        text_label = ttk.Label(title_frame, text=" 统计结果")
        text_label.pack(side=tk.LEFT)

        self.frame = ttk.LabelFrame(parent, labelwidget=title_frame, padding="10")
        self.frame.grid_columnconfigure(0, weight=1) # 调整列权重以适应新的布局
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)
        self.frame.grid_columnconfigure(3, weight=1)
        self.frame.grid_columnconfigure(4, weight=1)

        # 基础信息标签
        self.basic_info_frame = ttk.Frame(self.frame)
        self.basic_info_frame.grid(column=0, row=0, sticky="ew", pady=5)
        
        # 创建一个框架来容纳姿态统计信息
        self.pose_stats_frame = ttk.Frame(self.frame)
        self.pose_stats_frame.grid(column=0, row=1, sticky="ew", pady=5)
        
        # 创建一个框架来容纳警告信息
        self.warning_frame = ttk.Frame(self.frame)
        self.warning_frame.grid(column=0, row=2, sticky="ew", pady=5)
        
        # 基本信息变量
        self.var = StringVar()
        self.display = ttk.Label(self.basic_info_frame, textvariable=self.var, 
                               font=(customFont.get_name(), int(base_font * 0.7)))
        self.display.pack(anchor=tk.W)
        
        # 姿态统计标签 - 使用水平排列
        self.stats_title = ttk.Label(self.pose_stats_frame, text="姿态检测统计：", 
                                  font=(customFont.get_name(), int(base_font * 0.7), 'bold'))
        self.stats_title.grid(column=0, row=0, sticky=tk.W, padx=5)
        
        # 为不同姿态创建带颜色的标签
        self.person_label = tk.Label(self.pose_stats_frame, text="", bg='#f5f5f7', 
                                  font=(customFont.get_name(), int(base_font * 0.7)), highlightthickness=2, highlightbackground="#f5f5f7") # 默认边框
        self.person_label.grid(column=1, row=0, sticky=tk.W, padx=5)
        
        self.head_up_label = tk.Label(self.pose_stats_frame, text="", bg='#f5f5f7', fg='#007aff', 
                                    font=(customFont.get_name(), int(base_font * 0.7)))
        self.head_up_label.grid(column=2, row=0, sticky=tk.W, padx=10)
        
        self.head_down_label = tk.Label(self.pose_stats_frame, text="", bg='#f5f5f7', fg='#ff9500', 
                                      font=(customFont.get_name(), int(base_font * 0.7)))
        self.head_down_label.grid(column=3, row=0, sticky=tk.W, padx=10)
        
        self.lying_label = tk.Label(self.pose_stats_frame, text="", bg='#f5f5f7', fg='#ff3b30', 
                                  font=(customFont.get_name(), int(base_font * 0.7)))
        self.lying_label.grid(column=4, row=0, sticky=tk.W, padx=10)
        
        self.hand_label = tk.Label(self.pose_stats_frame, text="", bg='#f5f5f7', fg='#34c759', 
                                 font=(customFont.get_name(), int(base_font * 0.7)))
        self.hand_label.grid(column=5, row=0, sticky=tk.W, padx=10)
        
        # 警告标签
        self.warning_label = tk.Label(self.warning_frame, text="", bg='#f5f5f7', fg='#ff3b30', 
                                    font=(customFont.get_name(), int(base_font * 0.7), 'bold'))
        self.warning_label.pack(anchor=tk.W)
    
    def update_stats(self, basic_info, person_stat=None, head_up_stat=None, 
                     head_down_stat=None, lying_stat=None, hand_stat=None, warning=None, is_low_head_or_lying=False):
        """更新统计信息显示"""
        # 更新基本信息
        self.var.set(basic_info)
        
        # 更新姿态统计
        if person_stat:
            self.person_label.config(text=f"Person: {person_stat}")
            if is_low_head_or_lying:
                self.person_label.config(highlightbackground="red", highlightcolor="red")
            else:
                self.person_label.config(highlightbackground="#f5f5f7", highlightcolor="#f5f5f7") # 恢复默认边框

        if head_up_stat:
            self.head_up_label.config(text=f"Head Up: {head_up_stat}")
        if head_down_stat:
            self.head_down_label.config(text=f"Head Down: {head_down_stat}")
        if lying_stat:
            self.lying_label.config(text=f"Lying: {lying_stat}")
        if hand_stat:
            self.hand_label.config(text=f"Raise Hand: {hand_stat}")
        
        # 更新警告信息
        if warning:
            self.warning_label.config(text=warning)
        else:
            self.warning_label.config(text="")

class PoseRatioFrame:
    def __init__(self, parent, window_width, window_height, base_font):
        # 加载图标
        try:
            self.icon_image_pil = Image.open("static/ratio_icon.png").resize((20, 20), resample_lanczos)
            self.icon_image = ImageTk.PhotoImage(self.icon_image_pil)
        except Exception as e:
            print(f"Error loading ratio_icon.png: {e}")
            self.icon_image = None

        self.frame = ttk.LabelFrame(parent, text=" 姿态比例分析", padding="10")
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        
        # 创建三个子图的布局
        self.fig, self.axes = plt.subplots(3, 1, figsize=(window_width/150, window_height/250), sharex=True)
        self.fig.subplots_adjust(hspace=0.4)  # 调整子图间距
        
        # 设置图表字体大小和样式
        plt.rcParams.update({
            'font.size': int(base_font * 0.7),
            'font.family': customFont.get_name(),
            'axes.titlesize': int(base_font * 0.8),
            'axes.labelsize': int(base_font * 0.7),
            'xtick.labelsize': int(base_font * 0.6),
            'ytick.labelsize': int(base_font * 0.6)
        })
        
        # 设置三个子图的标题和标签
        self.axes[0].set_title('抬头率', fontweight='bold', color='#007aff')
        self.axes[1].set_title('举手率', fontweight='bold', color='#34c759')
        self.axes[2].set_title('低头+趴卧率', fontweight='bold', color='#ff3b30')
        
        # 初始化三个水平条形图
        self.head_up_bar = self.axes[0].barh([0], [0], color='#007aff', alpha=0.7)
        self.hand_up_bar = self.axes[1].barh([0], [0], color='#34c759', alpha=0.7)
        self.head_down_bar = self.axes[2].barh([0], [0], color='#ff3b30', alpha=0.7)
        
        # 设置Y轴标签
        for ax in self.axes:
            ax.set_yticks([])
            ax.set_xlim(0, 100)
            ax.grid(True, axis='x', linestyle='--', alpha=0.7)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
        
        # 设置X轴标签只在最后一个子图显示
        self.axes[2].set_xlabel('百分比 (%)')
        
        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def update_bars(self, head_up_rate, hand_up_rate, head_down_rate):
        """更新三个水平条形图的数据"""
        # 更新抬头率条形图
        self.head_up_bar[0].set_width(head_up_rate)
        self.axes[0].set_title(f'抬头率: {head_up_rate:.1f}%', fontweight='bold', color='#007aff')
        
        # 更新举手率条形图
        self.hand_up_bar[0].set_width(hand_up_rate)
        self.axes[1].set_title(f'举手率: {hand_up_rate:.1f}%', fontweight='bold', color='#34c759')
        
        # 更新低头+趴卧率条形图
        self.head_down_bar[0].set_width(head_down_rate)
        self.axes[2].set_title(f'低头+趴卧率: {head_down_rate:.1f}%', fontweight='bold', color='#ff3b30')
        
        # 重绘画布
        self.canvas.draw()

class ExportFrame:
    def __init__(self, parent, base_font):
        self.frame = ttk.Frame(parent)
        self.export_button = ttk.Button(self.frame, text="导出数据", style='TButton')
        self.export_button.pack(pady=10, padx=20, ipadx=10, ipady=5)


if __name__ == "__main__":
    app = MainWindow()
    app.run()