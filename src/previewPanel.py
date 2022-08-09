import wx
from cv2 import cvtColor, COLOR_BGR2RGB


class PreviewPanel(wx.Panel):
    def __init__(self, parent, size, object_detector):
        wx.Panel.__init__(self, parent, size=size)

        self.object_detector = object_detector

        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.w, self.h = size
        self.should_refresh = False

        wx.CallLater(50, self.check_refresh)

    # noinspection PyUnusedLocal
    def on_paint(self, event):
        dc = wx.PaintDC(self)

        if self.should_refresh:
            boxed_image = self.object_detector.draw_boxes()

            rgb_image = cvtColor(boxed_image, COLOR_BGR2RGB)

            dc.DrawBitmap(wx.Bitmap.FromBuffer(self.w, self.h, rgb_image), 0, 0)

    def check_refresh(self):
        self.on_paint(None)

        wx.CallLater(50, self.check_refresh)
