import cv2
from PIL import Image, ImageTk
from matplotlib import cm

class ImageProcessor:
    def __init__(self, imgSize):
        self.imgSize = imgSize

    def processFrame(self, frame, heatmap):
        frameResized = cv2.resize(frame, (self.imgSize, self.imgSize))
        img = cv2.cvtColor(frameResized, cv2.COLOR_BGR2RGB)
        jet = getattr(cm, 'jet', None)
        if jet is not None:
            heatmapColor = (jet(heatmap) * 255).astype('uint8')
        else:
            heatmapColor = (cm.get_cmap('jet')(heatmap) * 255).astype('uint8')
        overlay = cv2.addWeighted(img, 1.0, heatmapColor[:,:,:3], 0.3, 0)
        imgPil = Image.fromarray(overlay)
        return ImageTk.PhotoImage(imgPil)

    def getResizedFrame(self, frame):
        frameResized = cv2.resize(frame, (self.imgSize, self.imgSize))
        greyResized = cv2.cvtColor(frameResized, cv2.COLOR_BGR2GRAY)
        return frameResized, greyResized
