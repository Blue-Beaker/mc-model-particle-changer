import sys,os,shutil,configparser
from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import QApplication,QFileDialog,QWidget

dir=os.path.dirname(sys.argv[0])
os.chdir(dir)
sys.path.append(dir)
ui=os.path.join(dir,"main.ui")

cfgParser=configparser.ConfigParser()
cfgParser.read("main.cfg")
if not cfgParser.has_section("Temporary"):
    cfgParser.add_section("Temporary")

def writeConfig():
    with open("main.cfg","w") as f:
        cfgParser.write(f)

class Ui(QtWidgets.QMainWindow):
    fileChooserButton:QtWidgets.QPushButton
    folderSetButton:QtWidgets.QPushButton
    saveButton:QtWidgets.QPushButton
    cancelButton:QtWidgets.QPushButton
    workFolderInput:QtWidgets.QLineEdit
    fileList:QtWidgets.QListWidget
    texturePicker:QtWidgets.QListWidget
    texturePreview:QtWidgets.QGraphicsView

    folder:str
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi(ui, self)
        self.workFolderInput.setText(cfgParser.get("Temporary","last_used_path",fallback=""))

        self.fileChooserButton.clicked.connect(self.chooseFolder)
        self.folderSetButton.clicked.connect(self.setFolder)
        self.fileList.itemSelectionChanged.connect(self.selectFile)
        self.show()

    def setFolder(self):
        self.folder=self.workFolderInput.text()
        cfgParser.set("Temporary","last_used_path",self.folder)
        writeConfig()
        self.listDirToShow(self.folder)
    def chooseFolder(self):
        dialog=QFileDialog(self,directory=self.workFolderInput.text())
        dialog.setFileMode(QFileDialog.FileMode.DirectoryOnly)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly,False)
        dialog.fileSelected.connect(self.setFolderFromDialog)
        dialog.show()
    def setFolderFromDialog(self,path:str):
        self.workFolderInput.setText(path)
        self.setFolder()

    def listDirToShow(self,folder:str):
        self.fileList.clear()
        files=os.listdir(folder)
        files.sort()
        for file in files:
            self.fileList.addItem(file)
    
    def selectFile(self):
        for item in self.fileList.selectedItems():
            print(item.text())


app = QtWidgets.QApplication(sys.argv)
window=Ui()
# window = uic.loadUi(ui)
# if window==None:
#     exit()

window.show()
app.exec()