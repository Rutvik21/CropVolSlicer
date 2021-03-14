from __main__ import vtk, qt, ctk, slicer

class CropVol:
    def __init__(self, parent):
        parent.title = "Crop Vol Task"
        parent.categories = ["Example"]
        parent.dependencies = []
        parent.contributors = ["Rutvik Chauhan"]
        parent.helpText = "Task of creating module to crop volume"
        self.parent = parent


class CropVolWidget:
    def __init__(self, parent = None):
        if not parent:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
            self.parent.setMRMLScene(slicer.mrmlscene)

        else:
            self.parent = parent

        self.layout = self.parent.layout()

        if not parent:
            self.setup()
            self.parent.show()

    def setup(self):
        ##roi node
        self.roi_node = slicer.vtkMRMLAnnotationROINode()
        self.roi_node.Initialize(slicer.mrmlScene)
        self.roi_node.SetXYZ(0,0,0)
        self.roi_node.SetRadiusXYZ(0,0,0)

        #GUI
        self.cropCollapsibleButton = ctk.ctkCollapsibleButton()
        self.cropCollapsibleButton.text = "Crop Volume"
        self.layout.addWidget(self.cropCollapsibleButton)

        self.cropFormLayout = qt.QFormLayout(self.cropCollapsibleButton)

        #input volume selector
        self.inputFrame = qt.QFrame(self.cropCollapsibleButton)
        self.inputFrame.setLayout(qt.QHBoxLayout())
        self.cropFormLayout.addRow("Input Volume:", self.inputFrame)
        self.inputSelector = slicer.qMRMLNodeComboBox(self.inputFrame)
        self.inputSelector.nodeTypes = (("vtkMRMLScalarVolumeNode"),"")
        self.inputSelector.addEnabled = False
        self.inputSelector.removeEnabled = False
        self.inputSelector.setMRMLScene(slicer.mrmlScene)
        self.inputFrame.layout().addWidget(self.inputSelector)

        # slider
        self.slider = ctk.ctkSliderWidget()
        self.slider.decimals = 0
        self.slider.enabled = True
        self.cropFormLayout.addRow("ROI radius:", self.slider)

        self.slider.connect('valueChanged(double)', self.onSliderValueChanged)

        # Apply button
        cropVolButton = qt.QPushButton("Apply crop")
        cropVolButton.toolTip = "Apply the cropping on volume"
        self.cropFormLayout.addWidget(cropVolButton)
        cropVolButton.connect('clicked(bool)', self.onApply)

        self.layout.addStretch(1)

        self.cropVolButton = cropVolButton

    def onApply(self):
        inputVolume = self.inputSelector.currentNode()
        if not inputVolume:
            qt.QMessageBox.critical(slicer.util.mainWindow(), 'Crop Vol', 'Input volume required for crop vol')
            return
        
        cropVolLogic = slicer.modules.cropvolume.logic()
        cropVolParams = slicer.vtkMRMLCropVolumeParametersNode()
        cropVolParams.SetROINodeID(self.roi_node.GetID())
        cropVolParams.SetInputVolumeNodeID(inputVolume.GetID())
        #cropVolParams.SetVoxelBased(True)
        cropVolLogic.Apply(cropVolParams)

        croppedVolume = slicer.mrmlScene.GetNodeByID(cropVolParams.GetOutputVolumeNodeID())

        selectionNode = slicer.app.applicationLogic().GetSelectionNode()
        selectionNode.SetReferenceActiveVolumeID(croppedVolume.GetID())
        slicer.app.applicationLogic().PropagateVolumeSelection(0)

    def onSliderValueChanged(self, value):
        self.roi_node.SetRadiusXYZ(int(value),int(value),int(value))
        
