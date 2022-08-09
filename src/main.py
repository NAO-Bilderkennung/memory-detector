import wx

import appFrame

if __name__ == '__main__':
    app = wx.App(False)
    frame = appFrame.AppFrame(None, 'Memory Detector')
    frame.Show(True)

    app.MainLoop()
