from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication,QFileDialog
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import sys
import vtk


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow") #记录name
        MainWindow.resize(603, 553) #大小
        self.centralWidget = QtWidgets.QWidget(MainWindow)

        self.gridlayout = QtWidgets.QGridLayout(self.centralWidget)
        self.vtkWidget = QVTKRenderWindowInteractor(self.centralWidget)

        '''
        QT界面部分
        '''
        self.gridlayout.addWidget(self.vtkWidget, 0, 0, 100, 100)
        self.buttonLeft = QtWidgets.QPushButton("导入dicom文件夹")

        self.gridlayout.addWidget(self.buttonLeft, 96, 48, 1, 1)
        self.buttonRight = QtWidgets.QPushButton("导入mhd文件")

        self.gridlayout.addWidget(self.buttonRight, 96, 52, 1, 1)
        self.buttonUp = QtWidgets.QPushButton("导入vtk文件")

        self.gridlayout.addWidget(self.buttonUp, 94, 50, 1, 1)
        self.buttonDown = QtWidgets.QPushButton("导出图像")

        self.gridlayout.addWidget(self.buttonDown, 98, 50, 1, 1)
        self.buttonFire = QtWidgets.QPushButton("绘制")
        self.gridlayout.addWidget(self.buttonFire, 95, 50, 3, 1)
        MainWindow.setCentralWidget(self.centralWidget)


class SimpleView(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #UI绑定
        self.ui.buttonLeft.clicked.connect(self.dir_msg)
        # self.ui.buttonRight.clicked.connect(self.mhd_dir_msg)
        # self.ui.buttonUp.clicked.connect(self.vtk_dir_msg)
        # self.ui.buttonDown.clicked.connect(self.out_dir_msg)
        self.dir = ""
        self.vtk_dir = ""
        self.mhd_dir = ""


        self.ren = vtk.vtkRenderer()
        self.ui.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.ui.vtkWidget.GetRenderWindow().GetInteractor()
        #以下都是VTK绘制三维图像的正常操作
        # skin部分是绘制的具体图形
        v16 = vtk.vtkDICOMImageReader()
        v16.SetDataByteOrderToLittleEndian()
        v16.SetDirectoryName("F:/dcmdata")
        v16.SetDataSpacing(3.2, 3.2, 1.5)

        skinExtractor = vtk.vtkContourFilter()
        skinExtractor.SetInputConnection(v16.GetOutputPort())
        skinExtractor.SetValue(0, 500)
        skinNormals = vtk.vtkPolyDataNormals()
        skinNormals.SetInputConnection(skinExtractor.GetOutputPort())
        skinNormals.SetFeatureAngle(60.0)
        skinMapper = vtk.vtkPolyDataMapper()
        skinMapper.SetInputConnection(skinNormals.GetOutputPort())
        skinMapper.ScalarVisibilityOff()

        skin = vtk.vtkActor()
        skin.SetMapper(skinMapper)

        #outlineData是限制框
        outlineData = vtk.vtkOutlineFilter()
        outlineData.SetInputConnection(v16.GetOutputPort())

        #source = vtk.vtkSphereSource()
        #source.SetCenter(0, 0, 0)
        #source.SetRadius(5.0)

        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(outlineData.GetOutputPort())

        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        actor.GetProperty().SetColor(0, 0, 0)

        aCamera = vtk.vtkCamera()
        aCamera.SetViewUp(0, 0, -1)
        aCamera.SetPosition(0, 1, 0)
        aCamera.SetFocalPoint(0, 0, 0)
        aCamera.ComputeViewPlaneNormal()


        self.ren.AddActor(actor)
        self.ren.AddActor(skin)

        self.ren.SetActiveCamera(aCamera)
        self.ren.ResetCamera()
        aCamera.Dolly(1.5)

        self.ren.SetBackground(1, 1, 1)
        self.ren.ResetCameraClippingRange()

    def dir_msg(self):
        self.dir = QFileDialog.getExistingDirectory(self,"选取文件夹","./")

    #def vtk_dir_msg(self):




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleView()
    window.show() #这里其实并没有绘制但是显示了Qt的窗口
    window.iren.Initialize()  # Need this line to actually show the render inside Qt
    sys.exit(app.exec_())
