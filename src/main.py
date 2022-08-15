import wx

import appFrame

from downloadFrame import check_and_download_weights

if __name__ == '__main__':
    app = wx.App(False)

    frame = appFrame.AppFrame(None, 'Memory Detector')

    if not check_and_download_weights(frame):
        exit(1)

    frame.start_detection()

    app.MainLoop()
