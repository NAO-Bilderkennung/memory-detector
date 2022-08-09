import wx


class InfoPanel(wx.Panel):
    def __init__(self, parent, size, object_detector, grid_finder):
        wx.Panel.__init__(self, parent, size=size)

        self.object_detector = object_detector
        self.grid_finder = grid_finder
        self.should_refresh = False

        self.propTime = wx.StaticText(self, label='Forward propagation: TBD')
        self.extractionTime = wx.StaticText(self, label='Box extraction: TBD')
        self.drawingTime = wx.StaticText(self, label='Drawing time: TBD')
        self.gridTime = wx.StaticText(self, label='Grid finding time: TBD')

        self.useTestImage = wx.CheckBox(self, label='Use test image')
        self.useTestImage.SetValue(True)
        self.emulateNao = wx.CheckBox(self, label='Emulate NAO resolution')
        self.bwImage = wx.CheckBox(self, label='Use BW image')

        self.objectList = wx.ListCtrl(self, size=(-1, 200), style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.objectList.InsertColumn(0, 'Class')
        self.objectList.InsertColumn(1, 'Confidence')
        self.objectList.InsertColumn(2, 'Row')
        self.objectList.InsertColumn(3, 'Column')

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self.propTime)
        sizer.Add(self.extractionTime)
        sizer.Add(self.drawingTime)
        sizer.Add(self.gridTime)
        sizer.AddSpacer(10)
        sizer.Add(self.useTestImage)
        sizer.Add(self.emulateNao)
        sizer.Add(self.bwImage)
        sizer.AddSpacer(10)
        sizer.Add(self.objectList)

        self.SetSizer(sizer)

        wx.CallLater(50, self.check_refresh)

    def check_refresh(self):
        if not self.should_refresh:
            wx.CallLater(50, self.check_refresh)

        self.propTime.SetLabel(f'Forward propagation: {self.object_detector.propagationTime * 1000:.0f}ms')
        self.extractionTime.SetLabel(f'Box extraction: {self.object_detector.extractionTime * 1000:.0f}ms')
        self.drawingTime.SetLabel(f'Drawing time: {self.object_detector.drawingTime * 1000:.0f}ms')
        self.gridTime.SetLabel(f'Grid finding time: {self.grid_finder.runtime * 1000:.0f}ms')

        self.objectList.DeleteAllItems()

        for i in range(len(self.grid_finder.grid)):
            for j in range(len(self.grid_finder.grid[i])):
                (pos, size, class_name, confidence) = self.grid_finder.grid[i][j]

                self.objectList.Append((class_name, f'{confidence:.4f}', i, j))

        self.should_refresh = False

        wx.CallLater(50, self.check_refresh)
