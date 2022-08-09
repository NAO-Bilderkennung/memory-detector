import threading

import wx
from cv2 import imread, resize, cvtColor, COLOR_BGR2GRAY, COLOR_GRAY2BGR

import camera
import detection.yolo as yolo
import detection.grid as grid
import infoPanel
import previewPanel


class AppFrame(wx.Frame):
    ID_REFRESH = wx.NewIdRef(count=1)

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1000, 550))

        self.testImage = imread('test.png')

        self.webcam, self.webcam_width, self.webcam_height = camera.get_camera()
        self.w, self.h = 640, 480

        self.object_detector = yolo.ObjectDetector(self.w, self.h)
        self.grid_finder = grid.GridFinder(self.w, self.h)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.previewPanel = previewPanel.PreviewPanel(self, size=(640, 550), object_detector=self.object_detector)
        self.infoPanel = infoPanel.InfoPanel(self, size=(360, 550), object_detector=self.object_detector,
                                             grid_finder=self.grid_finder)

        self.detected_image = None

        sizer.Add(self.previewPanel)
        sizer.Add(self.infoPanel)

        self.SetSizer(sizer)

        self.Show(True)

        self.refresh_thread = threading.Thread(target=self.detect_and_set_refresh, daemon=True)
        self.refresh_thread.start()

    def detect_and_set_refresh(self):
        while True:
            if not self.infoPanel.useTestImage.IsChecked():
                ret, image = self.webcam.read()
            else:
                image = self.testImage
                image = resize(image, (640, 480))

            if self.infoPanel.emulateNao.IsChecked():
                image = resize(image, (320, 240))

                w, h = 320, 240
            else:
                w, h = self.webcam_width, self.webcam_height

            if self.infoPanel.bwImage.IsChecked():
                image = cvtColor(image, COLOR_BGR2GRAY)
                image = cvtColor(image, COLOR_GRAY2BGR)

            self.previewPanel.SetSize(w, h)

            self.object_detector.w, self.object_detector.h = w, h
            self.grid_finder.w, self.grid_finder.h = w, h
            self.previewPanel.w, self.previewPanel.h = w, h

            self.object_detector.detect(image)
            self.grid_finder.calculate_grid_positions(self.object_detector.boundingBoxes)

            self.previewPanel.should_refresh = True
            self.infoPanel.should_refresh = True
