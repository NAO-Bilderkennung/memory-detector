import os.path
from threading import Thread

import wx
from wx.lib.pubsub import pub
from urllib import request

weights_url = 'https://pjreddie.com/media/files/yolov3.weights'


class DownloadThread(Thread):
    def __init__(self):
        Thread.__init__(self)

        self.resp = request.urlopen(weights_url)

        self.file_size = int(self.resp.headers['Content-Length'])
        self.dl_size = 0
        self.file = open('data/yolov3.weights', 'wb')

        self.start()

    def run(self):
        while self.dl_size < self.file_size:
            read_bytes = self.resp.read(4096)
            self.file.write(read_bytes)
            self.dl_size += len(read_bytes)

            new_label = f'Downloading \'yolov3.weights\' ({self.dl_size / 1e6:.1f} MB/{self.file_size / 1e6:.1f}MB)...'
            wx.CallAfter(pub.sendMessage, 'dl_thread', data=(self.dl_size / 1e6, self.file_size / 1e6, new_label))

        wx.CallAfter(pub.sendMessage, 'dl_thread_done')


class WeightsDownloaderProgressDialog(wx.ProgressDialog):
    def __init__(self, parent):
        wx.ProgressDialog.__init__(self, 'YOLOv3 weights', 'Preparing download...' + ('\u00a0' * 23), maximum=100,
                                   parent=parent, style=wx.PD_APP_MODAL | wx.CENTRE)

        self.is_closed = False

        pub.subscribe(self.on_download_updated, 'dl_thread')
        pub.subscribe(self.on_download_finished, 'dl_thread_done')

        self.thread = DownloadThread()

    def on_download_updated(self, data):
        dl_size, file_size, new_label = data
        self.SetRange(int(file_size))
        self.Update(int(dl_size), new_label)

    def on_download_finished(self):
        wx.MessageBox('Download finished!', 'YOLOv3 weights', parent=self)

        self.is_closed = True
        self.Close()

        pub.sendMessage('app_can_start')


def check_and_download_weights(parent):
    if os.path.exists('data/yolov3.weights'):
        return True

    resp = request.urlopen(weights_url)
    file_size = int(resp.headers['Content-Length'])

    answer = wx.MessageBox('The YOLOv3 weights couldn\'t be found. Do you want to download them?' +
                           f' (ca. {file_size / 1e6:.1f} MB)', 'YOLOv3 weights', wx.YES_NO | wx.CENTRE, parent)

    if answer == wx.NO:
        return False

    try:
        WeightsDownloaderProgressDialog(parent)

        return True
    except Exception as e:
        wx.MessageBox(f'An error occurred: {e}', 'Error', wx.ICON_ERROR | wx.OK)
        return False
