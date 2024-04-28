import sys,os,shutil,configparser,json,traceback
from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap,QResizeEvent
from PyQt5.QtCore import *

dir=os.path.dirname(sys.argv[0])
os.chdir(dir)
sys.path.append(dir)
from modelparser import *

ui=os.path.join(dir,"main.ui")

cfgParser=configparser.ConfigParser()
cfgParser.read("main.cfg")
if not cfgParser.has_section("Temporary"):
    cfgParser.add_section("Temporary")

def writeConfig():
    with open("main.cfg","w") as f:
        cfgParser.write(f)

class App(QtWidgets.QMainWindow):
    fileChooserButton:QtWidgets.QPushButton
    folderSetButton:QtWidgets.QPushButton
    saveButton:QtWidgets.QPushButton
    setParticleButton:QtWidgets.QPushButton
    workFolderInput:QtWidgets.QLineEdit
    fileList:QtWidgets.QTableWidget
    texturePicker:QtWidgets.QTableWidget
    texturePreview:QtWidgets.QGraphicsView
    horizontalLayout:QtWidgets.QHBoxLayout
    centralwidget:QtWidgets.QWidget
    textureLabel:QtWidgets.QLabel

    folder:str=""
    currentFile:str=""
    data:dict={}
    textureFile:str=""
    packroot:str=""
    textures:dict={}
    def __init__(self):
        super(App, self).__init__()
        uic.loadUi(ui, self)
        self.workFolderInput.setText(cfgParser.get("Temporary","last_used_path",fallback="")
)
        self.centralWidget().setLayout(self.horizontalLayout)

        self.fileChooserButton.clicked.connect(self.chooseFolder)
        self.folderSetButton.clicked.connect(self.setFolder)
        self.fileList.itemSelectionChanged.connect(self.selectFile)
        self.texturePicker.itemSelectionChanged.connect(self.selectTexture)

        self.setParticleButton.clicked.connect(self.setAsParticle)
        self.saveButton.clicked.connect(self.saveToFile)

        self.show()
        
    def resizeEvent(self, event:QResizeEvent):
        new_size = event.size()
        self.updateTexture()

    def setFolder(self):
        self.folder=self.workFolderInput.text()
        cfgParser.set("Temporary","last_used_path",self.folder)
        writeConfig()
        self.packroot=getRootDir(self.folder)
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

    def listDirRecursive(self,folder:str):
        files=os.listdir(folder)
        files.sort()
        files2=[]
        files3=[]
        for file in files:
            absfile=os.path.join(folder,file)
            if os.path.isdir(absfile):
                for file2 in self.listDirRecursive(absfile):
                    files2.append(os.path.join(file,file2))
            elif file.endswith(".json"):
                files3.append(file)
        files2.extend(files3)
        return files2

    def listDirToShow(self,folder:str):
        self.fileList.clearContents()
        self.fileList.setRowCount(0)
        # files=os.listdir(folder)
        files=self.listDirRecursive(folder)
        # files.sort()
        for file in files:
            row = self.fileList.rowCount()
            self.fileList.insertRow(row)
            self.fileList.setItem(row,0,QTableWidgetItem(file))
            with open(os.path.join(self.folder,file),"r") as f:
                data=json.load(f)
            self.fileList.setItem(row,1,QTableWidgetItem(
                lookupParentParticle(self.packroot,data)))
    
    def readFile(self,path):
        try:
            f=open(os.path.join(self.folder,path),"r")
            data=json.load(f)
            f.close()
            return data
        except:
            traceback.format_exc()
            return {}
        
    def selectFile(self):
        file=self.fileList.selectedItems()[0].text()
        self.currentFile=file
        self.data=self.readFile(file)
        # print(file)
        self.showTextures()

    def showTextures(self):
        self.textures=self.listTextures()
        textures=copy.deepcopy(self.textures)
        self.texturePicker.clearContents()
        self.texturePicker.setRowCount(0)
        for key in textures:
            row = self.texturePicker.rowCount()
            self.texturePicker.insertRow(row)
            self.texturePicker.setItem(row,0,QTableWidgetItem(key))
            self.texturePicker.setItem(row,1,QTableWidgetItem(textures[key]))

    def listTextures(self):
        data=self.data
        return getAllTextures(data)
    
    def selectTexture(self):
        selected=self.texturePicker.selectedItems()
        if selected.__len__()<2:
            return
        texture=selected[1].text()
        textureFile=self.lookupTexture(texture)
        # print(textureFile)
        self.textureFile=textureFile
        self.updateTexture()

    def updateTexture(self):
        self.textureLabel.setText(getResourceLocation(self.packroot,self.textureFile))
        def getScale(pix:QWidget,view:QWidget):
            pw=pix.width()
            ph=pix.height()
            if pw==0 or ph==0:
                return 1
            vw=view.width()-10
            vh=view.height()-10
            
            return min(vw/pw,vh/ph)

        pix = QPixmap(self.textureFile)
        item = QtWidgets.QGraphicsPixmapItem(pix)
        item.setScale(getScale(pix,self.texturePreview))
        scene = QtWidgets.QGraphicsScene(self)
        scene.addItem(item)
        self.texturePreview.setScene(scene)

    def lookupTexture(self,texture:str):
        path=lookupTexture(self.packroot,texture,self.textures)
        return path
    
    def setAsParticle(self):
        selected=self.texturePicker.selectedItems()
        if selected.__len__()<2:
            return
        texture=selected[0].text()
        if texture.startswith("__e"):
            texture=selected[1].text()
        else:
            texture="#"+texture.removeprefix("#")
        self.data["textures"]["particle"]=texture
        self.showTextures()
    def saveToFile(self):
        data=self.data
        with open(os.path.join(self.folder,self.currentFile),"w") as f:
            json.dump(data,f,indent=2)
        row=self.fileList.currentRow()
        self.fileList.setItem(row,1,QTableWidgetItem(getParticle(self.readFile(self.currentFile))))



app = QtWidgets.QApplication(sys.argv)
window=App()
# window = uic.loadUi(ui)
# if window==None:
#     exit()

window.show()
app.exec()