import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon,QStandardItem,QStandardItemModel
from PyQt5.QtCore import QSize
from PyQt5.Qt import *
from File import *
import time
import os
import pickle
from MyWidget import MyListWidget
from fileEdit import editForm,attributeForm

#主窗体
class mainForm(QMainWindow):
    def __init__(self):
        super().__init__()

        """
        读取文件
        """
        self.readFile()

        #根目录
        self.curNode=self.catalog[0]#设置当前节点为目录的第一个结点
        self.rootNode=self.curNode#设置根节点为当前结点
        self.baseUrl=['root']#初始化根目录的URL

        """
        窗体基本信息
        """
        self.resize(1200,800)
        self.setWindowTitle('FileManagement')
        self.setWindowIcon(QIcon('img/folder.ico'))

        #窗口居中
        qr=self.frameGeometry()
        centerPlace=QDesktopWidget().availableGeometry().center()
        qr.moveCenter(centerPlace)
        self.move(qr.topLeft())

        #窗口布局
        grid=QGridLayout()#创建网格布局
        grid.setSpacing(10)#设置网格间距
        self.widGet=QWidget()
        self.widGet.setLayout(grid)
        self.setCentralWidget(self.widGet)
        
        #退出事件
        exitAction = QAction(QIcon('file.png'), '退出', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)

        #菜单栏
        menubar=self.menuBar()
        #添加菜单
        fileMenu=menubar.addMenu('文件')
        #添加事件
        fileMenu.addAction(exitAction)
        
        menubar.addAction('格式化', self.format)
        

        """
        添加工具栏
        """

        #返回键
        self.backAction=QAction(QIcon('img/back.png'), '&上一级',self)
        exitAction.setShortcut('Ctrl+E')#返回快捷键
        self.backAction.triggered.connect(self.backEvent)
        self.toolBar=self.addToolBar('工具栏')
        self.toolBar.addAction(self.backAction)
        self.backAction.setEnabled(False)

        #前进键
        self.forwardAction=QAction(QIcon('img/forward.png'), '&下一级',self)
        self.forwardAction.triggered.connect(self.forwardEvent)
        self.toolBar.addAction(self.forwardAction)
        self.forwardAction.setEnabled(False)

        self.toolBar.addSeparator()

        #当前所在路径
        self.curLocation=QLineEdit()
        self.curLocation.setText('> root')
        self.curLocation.setReadOnly(True)

        #图标
        self.curLocation.addAction(QIcon('img/folder.png'), QLineEdit.LeadingPosition)

        self.curLocation.setMinimumHeight(40)
        ptrLayout=QFormLayout()
        ptrLayout.addRow(self.curLocation)

        ptrWidget=QWidget()

        ptrWidget.setLayout(ptrLayout) 
        ptrWidget.adjustSize()
        #设置自动补全
        self.toolBar.addWidget(ptrWidget)

        self.toolBar.setMovable(False)

        """
        左侧地址栏
        """

        #左侧的地址栏
        self.tree=QTreeWidget()
        #设置列数
        self.tree.setColumnCount(1)
        #设置标题
        self.tree.setHeaderLabels(['目录'])
        #建树
        self.buildTree()
        #设置选中状态
        self.tree.setCurrentItem(self.rootItem)
        #设置当前路径
        self.treeItem=[self.rootItem]
        #绑定单击事件
        self.tree.itemClicked['QTreeWidgetItem*','int'].connect(self.clickTreeItem)

        grid.addWidget(self.tree,1,0)


        """
        文件基本信息
        """
        self.listView=MyListWidget(self.curNode,parents=self)
        self.listView.setMinimumWidth(800)
        self.listView.setViewMode(QListView.IconMode)
        self.listView.setIconSize(QSize(72,72))
        self.listView.setGridSize(QSize(100,100))
        self.listView.setResizeMode(QListView.Adjust)
        self.listView.setMovement(QListView.Static)
        self.listView.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.listView.doubleClicked.connect(self.openFile)

        #加载当前路径文件
        self.loadCurFile()
        grid.addWidget(self.listView, 1, 1)

       

        """
        右击菜单
        """

        self.listView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listView.customContextMenuRequested.connect(self.show_menu)

        """
        美化
        """
        self.updatePrint()
        self.lastLoc=-1

        #删除文件快捷键
        QShortcut(QKeySequence(self.tr("Delete")), self, self.deleteFile)
    

    def clickTreeItem(self,item,column):
        #初始化一个列表，并将当前点击的项加入列表
        ways=[item]
        #初始化层数变量
        level=0
        temp=item
        
        #逐级遍历父节点，并将父节点加入列表
        while temp.parent()!=None:
            temp=temp.parent()
            ways.append(temp)
            level+=1

        #翻转得到从树根到点击项的路径
        ways.reverse()
        #回退到根节点
        while self.backEvent():
            pass
        self.baseUrl=self.baseUrl[:1]#重置项目路径和Item列表
        self.treeItem=self.treeItem[:1]

        #逐步前进到点击的项
        for i in ways:
            if i==self.rootItem:
                continue
            #前往该路径
            #从curNode的子结点中查询item
            newNode=None
            for j in self.curNode.children:
                if j.name==i.text(0):
                    newNode=j
                    break
            #前往路径j
            if newNode.isFile:
                #如果是文件则跳出循环
                break
            else:
                self.curNode=newNode#否则更新当前结点及路径
                self.updateLoc()
                self.baseUrl.append(newNode.name)

                #更新
                for j in range(self.treeItem[-1].childCount()):
                    if self.treeItem[-1].child(j).text(0)==newNode.name:
                        selectedItem=self.treeItem[-1].child(j)
                self.treeItem.append(selectedItem)
                self.tree.setCurrentItem(selectedItem)
        
        #更新界面
        self.updatePrint()
        
        #如果当前结点不是根节点，则back按钮可使用
        if self.curNode!=self.rootNode:
            self.backAction.setEnabled(True)
        
        #前进按钮不可使用
        self.forwardAction.setEnabled(False)
        self.lastLoc=-1#将lastLoc重置为-1

    def updateLoc(self):
        self.loadCurFile()#加载当前结点的文件
        self.listView.curNode=self.curNode#更新listView中的当前结点

    """
    打开文件
    """
    def openFile(self,modelindex: QModelIndex)->None:
        #关闭列表视图的编辑模式
        self.listView.close_edit()

        #获取用户点击的项
        try:
            item = self.listView.item(modelindex.row())
        except:
            #如果没有选中的项则直接返回
            if len(self.listView.selectedItems())==0:
                return
            #否则将item设置为最后一个选中的项
            item=self.listView.selectedItems()[-1]

        #如果有下一级文件且lastLoc不是默认值
        if self.lastLoc!=-1 and self.nextStep:
            #则将item设置为lastLoc对应的项
            item=self.listView.item(self.lastLoc)
            self.lastLoc=-1#重置lastLoc
            self.forwardAction.setEnabled(False)#并将前进按钮设置为不可使用
        self.nextStep=False

        newNode=None#初始化newNode
        #在当前结点的子结点中查找与item相同的项，并将其设置为newNode
        for i in self.curNode.children:
            if i.name==item.text():
                newNode=i
                break
        
        #如果newNode是文件，则读入数据
        if newNode.isFile:
            data=newNode.data.read(self.fat,self.disk)
            self.child=editForm(newNode.name, data)#创建编辑表单并显示文件名和数据
            self.child._signal.connect(self.getData)#连接表单的信号到getData方法
            self.child.show()#显示表单内容
            self.writeFile=newNode#将当前文件设置为newNode
        else:
            #进下一级目录前，如果处于编辑状态，先关闭编辑状态
            self.listView.close_edit()

            self.curNode=newNode#修改当前结点为newNode
            self.updateLoc()#更新Loc
            self.baseUrl.append(newNode.name)#向路径中加入newNode的名字

            #更新路径
            for i in range(self.treeItem[-1].childCount()):
                if self.treeItem[-1].child(i).text(0)==newNode.name:#在树项中找到newNode
                    selectedItem=self.treeItem[-1].child(i)#更新selectedItem
            self.treeItem.append(selectedItem)#将selectedItem添加到树项中
            self.tree.setCurrentItem(selectedItem)#设置当前项为selectedItem
            self.backAction.setEnabled(True)#启用返回上一级的按钮

            self.updatePrint()#更新界面

    #工具函数，用于更新路径
    def updatePrint(self):
        
        s='> root'
        #更新路径
        for i,item in enumerate(self.baseUrl):
            if i==0:
                continue
            s+=" > "+item
                
        self.curLocation.setText(s)
    """
    对文件或文件夹重命名
    """
    def rename(self):
        if len(self.listView.selectedItems())==0:
            return
        #获取最后一个被选中的
        self.listView.editSelected(self.listView.selectedIndexes()[-1].row())
        self.updateTree()

    """
    删除文件
    """
    def deleteFile(self):
        
        if len(self.listView.selectedItems())==0:
            return

        item=self.listView.selectedItems()[-1]
        index=self.listView.selectedIndexes()[-1].row()#获取被删除文件的索引

        #提示框
        reply=QMessageBox()
        reply.setWindowTitle('提示')

        if self.curNode.children[index].isFile:
            reply.setText('确定要删除文件'+item.text()+'吗？')
        else:
            reply.setText('确定要删除文件夹'+item.text()+'及其中所有内容吗？')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        buttonY = reply.button(QMessageBox.Yes)
        buttonY.setText('确定')
        buttonN = reply.button(QMessageBox.No)
        buttonN.setText('取消')

        reply.exec_()

        if reply.clickedButton()==buttonN:
            return
        
        #删除文件
        self.listView.takeItem(index)
        del item
        #删除fat表中的内容
        self.deleteFileRecursive(self.curNode.children[index])
        self.curNode.children.remove(self.curNode.children[index])
        #更新catalog表
        self.catalog=self.updateCatalog(self.rootNode)

        #更新左侧预览图
        self.updateTree()

    def deleteFileRecursive(self,node):
        if node.isFile:#如果是文件，则直接删除其中的所有数据
            node.data.delete(self.fat,self.disk)
        else:
            for i in node.children:#否则再遍历文件夹中的所有文件并进行删除
                self.deleteFileRecursive(i)
   
    #工具函数，更新Catalog
    def updateCatalog(self,node):
        if node.isFile:
            return [node]#返回一个包含该结点的列表
        else:#否则把子树中的所有结点都添加到列表中并返回
            x=[node]
            for i in node.children:
                x+=self.updateCatalog(i)
            return x
    """
    创建文件夹
    """
    def createFolder(self):

        self.item_1=QListWidgetItem(QIcon("img/folder.png"), "新建文件夹")
        self.listView.addItem(self.item_1)#在列表视图中显示新项
        self.listView.editLast()#允许用户对文件夹进行重命名

        #添加到目录表中
        #首先创建newNode用于表示该文件夹
        newNode=CatalogNode(self.item_1.text(),False,self.fat,self.disk,time.localtime(time.time()),self.curNode)
        self.curNode.children.append(newNode)#并将newNode添加到当前结点的子结点列表中
        self.catalog.append(newNode)

        #更新左侧预览图
        self.updateTree()
    """
    创建文件
    """
    def createFile(self):
        self.item_1=QListWidgetItem(QIcon("img/file.png"), "新建文件")
        self.listView.addItem(self.item_1)
        self.listView.editLast()

        #添加到目录表中
        newNode=CatalogNode(self.item_1.text(),True,self.fat,self.disk,time.localtime(time.time()),self.curNode)
        self.curNode.children.append(newNode)
        self.catalog.append(newNode)

        #更新左侧预览图
        self.updateTree()

    """
    查看属性
    """
    def viewAttribute(self):
        #查看当前路径属性
        if len(self.listView.selectedItems())==0:
            #创建attributeForm对象显示当前文件的属性
            self.child=attributeForm(self.curNode.name, False,self.curNode.createTime,self.curNode.updateTime,len(self.curNode.children))

            self.child.show()
            return
        else:
            #获取选中的最后一个
            node=self.curNode.children[self.listView.selectedIndexes()[-1].row()]
            if node.isFile:
                self.child=attributeForm(node.name, node.isFile,node.createTime,node.updateTime,0)
            else:
                self.child=attributeForm(node.name, node.isFile,node.createTime,node.updateTime,len(node.children))
            self.child.show()
            return

    
    def show_menu(self,point):
        menu=QMenu(self.listView)#创建右键菜单
        
        #如果点击的是文件或文件夹
        if len(self.listView.selectedItems())!=0:
            
            #添加菜单中的按钮
            openFileAction=QAction(QIcon(),'打开')
            openFileAction.triggered.connect(self.openFile)
            menu.addAction(openFileAction)

            deleteAction=QAction(QIcon(),'删除')
            deleteAction.triggered.connect(self.deleteFile)
            menu.addAction(deleteAction)


            renameAction=QAction(QIcon(),'重命名')
            renameAction.triggered.connect(self.rename)
            menu.addAction(renameAction)

            viewAttributeAction=QAction(QIcon('img/attribute.png'),'属性')
            viewAttributeAction.triggered.connect(self.viewAttribute)
            menu.addAction(viewAttributeAction)

            dest_point=self.listView.mapToGlobal(point)
            menu.exec_(dest_point)#将菜单显示在点击的位置

        else:#如果点击的是空白位置
            """
            查看
            """
            viewMenu=QMenu(menu)#创建子菜单查看
            viewMenu.setTitle('查看')
            #向子菜单中添加按钮，并给按钮关联点击后的动作（重置列表中项的大小）
            #大图标
            bigIconAction=QAction(QIcon(),'大图标')
            def bigIcon():
                self.listView.setIconSize(QSize(172,172))
                self.listView.setGridSize(QSize(200,200))
            bigIconAction.triggered.connect(bigIcon)
            viewMenu.addAction(bigIconAction)

            #中等图标
            middleIconAction=QAction(QIcon(),'中等图标')
            def middleIcon():
                self.listView.setIconSize(QSize(72,72))
                self.listView.setGridSize(QSize(100,100))
            middleIconAction.triggered.connect(middleIcon)
            viewMenu.addAction(middleIconAction)

            #小图标
            smallIconAction=QAction(QIcon(),'小图标')
            def smallIcon():
                self.listView.setIconSize(QSize(56,56))
                self.listView.setGridSize(QSize(84,84))
            smallIconAction.triggered.connect(smallIcon)
            viewMenu.addAction(smallIconAction)
            menu.addMenu(viewMenu)


            """
            新建
            """
            createMenu=QMenu(menu)#创建子菜单新建
            createMenu.setTitle('新建')

            #新建文件夹
            createFolderAction=QAction(QIcon('img/folder.png'),'文件夹')
            createFolderAction.triggered.connect(self.createFolder)
            createMenu.addAction(createFolderAction)

            #新建文件
            createFileAction=QAction(QIcon('img/file.png'),'文件')
            createFileAction.triggered.connect(self.createFile)
            createMenu.addAction(createFileAction)

            createMenu.setIcon(QIcon('img/create.png'))
            menu.addMenu(createMenu)


            """
            属性
            """
            viewAttributeAction=QAction(QIcon('img/attribute.png'),'属性')
            viewAttributeAction.triggered.connect(self.viewAttribute)
            menu.addAction(viewAttributeAction)

            self.nextStep=False
            

            dest_point=self.listView.mapToGlobal(point)
            menu.exec_(dest_point)#将菜单显示在点击位置

    def updateTree(self):
        node=self.rootNode#node为树的根结点对象
        item=self.rootItem#item为树形控件中的根结点项

        #如果控件中的子项数量小于结点中的子项数量
        if item.childCount()<len(node.children):
            #增加一个新item
            child=QTreeWidgetItem(item)
        #如果控件中的子项数量大于结点中的子项数量
        elif item.childCount()>len(node.children):
            #一个一个找，删除掉对应元素
            for i in range(item.childCount()):
                if i==item.childCount()-1:
                    item.removeChild(item.child(i))
                    break
                if item.child(i).text(0)!=node.children[i].name:
                    item.removeChild(item.child(i))
                    break

        for i in range(len(node.children)):
            self.updateTreeRecursive(node.children[i], item.child(i))

        self.updateTreeRecursive(node, item)

    def updateTreeRecursive(self,node:CatalogNode,item:QTreeWidgetItem):
        item.setText(0, node.name)#设置控件第一列的文本为结点node的名称
        if node.isFile:
            item.setIcon(0, QIcon('img/file.png'))
        else:
            #根据是否有子树设置图标
            if len(node.children)==0:
                item.setIcon(0, QIcon('img/folder.png'))
            else:
                item.setIcon(0, QIcon('img/folderWithFile.png'))
            if item.childCount()<len(node.children):
                #增加一个新item即可
                child=QTreeWidgetItem(item)
            elif item.childCount()>len(node.children):
                #一个一个找，删除掉对应元素
                for i in range(item.childCount()):
                    if i==item.childCount()-1:
                        item.removeChild(item.child(i))
                        break
                    if item.child(i).text(0)!=node.children[i].name:
                        item.removeChild(item.child(i))
                        break
            for i in range(len(node.children)):
                self.updateTreeRecursive(node.children[i], item.child(i))


    def buildTree(self):
        self.tree.clear()
        self.rootItem=self.buildTreeRecursive(self.catalog[0],self.tree)#传入根结点和控件，用于构建rootItem
        
        self.tree.addTopLevelItem(self.rootItem)#将rootItem添加到控件中
        self.tree.expandAll()#展开所有结点

    def getData(self, parameter):
        """
        向文件中写入新数据
        """
        self.writeFile.data.update(parameter,self.fat,self.disk)
        self.writeFile.updateTime=time.localtime(time.time())
        
    def buildTreeRecursive(self,node:CatalogNode,parent:QTreeWidgetItem):
        """
        目录树的建立
        """
        #创建子结点
        child=QTreeWidgetItem(parent)
        child.setText(0,node.name)
        #设置图标
        if node.isFile:
            child.setIcon(0,QIcon('img/file.png'))
        else:
            if len(node.children)==0:
                child.setIcon(0, QIcon('img/folder.png'))
            else:
                child.setIcon(0, QIcon('img/folderWithFile.png'))
            for i in node.children:
                self.buildTreeRecursive(i,child)
        
        return child


    def loadCurFile(self):
        """
        加载当前路径的文件
        """
        self.listView.clear()

        for i in self.curNode.children:#遍历当前结点的所有子结点并添加到列表中
            if i.isFile:
                self.item_1=QListWidgetItem(QIcon("img/file.png"), i.name)
                self.listView.addItem(self.item_1)
            else:
                if len(i.children)==0:
                    self.item_1=QListWidgetItem(QIcon("img/folder.png"), i.name)
                else:
                    self.item_1=QListWidgetItem(QIcon("img/folderWithFile.png"), i.name)
                self.listView.addItem(self.item_1)

    def format(self):
        """
        对象的格式化
        """ 
        #结束编辑
        self.listView.close_edit()

        #提示框
        reply=QMessageBox()
        reply.setWindowTitle('提醒')
        reply.setText('确定要格式化磁盘吗？(此操作不可逆！)')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        buttonY = reply.button(QMessageBox.Yes)
        buttonY.setText('确定')
        buttonN = reply.button(QMessageBox.No)
        buttonN.setText('取消')
        reply.exec_()
        reply.show()

        if reply.clickedButton()==buttonN:
            return
        
        """
        格式化文件
        """
        self.fat=FAT()#创建新的fat对象，将其初始化为全-2的列表并存储为二进制文件fat
        self.fat.fat=[-2]*blockNum
        #存储fat表
        with open('fat','wb') as f:
            f.write(pickle.dumps(self.fat))

        self.disk=[]#创建空的disk列表，向其中添加blockNum个block对象，然后将整个列表存储为二进制文件disk
        for i in range(blockNum):
            self.disk.append(Block(i))
        #存储disk表
        with open('disk','wb') as f:
            f.write(pickle.dumps(self.disk))
        
        self.catalog=[]#创建一个空的catalog列表，向其中添加一个名为root的根结点，初始化其中包含fat和disk，并存储为二进制文件
        self.catalog.append(CatalogNode("root", False, self.fat, self.disk, time.localtime(time.time())))
        #存储
        with open('catalog','wb') as f:
            f.write(pickle.dumps(self.catalog))

        self.hide()#隐藏当前窗口
        self.winform=mainForm()#显示新窗口
        self.winform.show()
        
    
    def saveFile(self):
        """
        将内存中的文件存到本地
        """
        #存储fat表
        with open('fat','wb') as f:
            f.write(pickle.dumps(self.fat))
        #存储disk表
        with open('disk','wb') as f:
            f.write(pickle.dumps(self.disk))
        #存储
        with open('catalog','wb') as f:
            f.write(pickle.dumps(self.catalog))

    def readFile(self):
        #读取fat表
        if not os.path.exists('fat'):
            self.fat=FAT()
            self.fat.fat=[-2]*blockNum
            #存储fat表
            with open('fat','wb') as f:
                f.write(pickle.dumps(self.fat))
        else:
            with open('fat','rb') as f:
                self.fat=pickle.load(f)

        #读取disk表
        if not os.path.exists('disk'):
            self.disk=[]
            for i in range(blockNum):
                self.disk.append(Block(i))
            #存储disk表
            with open('disk','wb') as f:
                f.write(pickle.dumps(self.disk))
        else:
            with open('disk','rb') as f:
                self.disk=pickle.load(f)

        #读取catalog表
        if not os.path.exists('catalog'):
            self.catalog=[]
            self.catalog.append(CatalogNode("root", False, self.fat, self.disk, time.localtime(time.time())))
            #存储
            with open('catalog','wb') as f:
                f.write(pickle.dumps(self.catalog))
        else:
            with open('catalog','rb') as f:
                self.catalog=pickle.load(f)

    def initial(self):
        # fat表
        self.fat=FAT()
        self.fat.fat=[-2]*blockNum
        #存储fat表
        with open('fat','ab') as f:
            f.write(pickle.dumps(self.fat))
        
        #disk表
        self.disk=[]
        for i in range(blockNum):
            self.disk.append(Block(i))
        #存储disk表
        with open('disk','ab') as f:
            f.write(pickle.dumps(self.disk))
        
        #catalogNode
        self.catalog=[]
        self.catalog.append(CatalogNode("root", False, self.fat, self.disk, time.localtime(time.time())))
        #存储
        with open('catalog','ab') as f:
            f.write(pickle.dumps(self.catalog))

    
    def backEvent(self):
        """
        返回上一级
        """
        self.listView.close_edit()

        if self.rootNode==self.curNode:
            #根节点无法返回
            return False


        #记录上次所在位置
        for i in range(len(self.curNode.parent.children)):
            if self.curNode.parent.children[i].name==self.curNode.name:
                self.lastLoc=i#找当前结点在父节点中的下标
                self.forwardAction.setEnabled(True)#允许通过forward按钮进入下一级
                break

        self.curNode=self.curNode.parent#修改当前结点为父节点
        self.updateLoc()
        self.baseUrl.pop()
        self.treeItem.pop()
        self.tree.setCurrentItem(self.treeItem[-1])#将当前项目设置为self.treeItem列表的最后一个元素
        self.updateTree()#更新树形结构
        self.updatePrint()#更新页面

        if self.curNode==self.rootNode:#如果当前结点为根结点，则不允许再点击back按钮
            self.backAction.setEnabled(False)
        
        

        return True

    def forwardEvent(self):
        self.nextStep=True
        self.openFile(QModelIndex())

    def closeEvent(self,event):
        #结束编辑
        self.listView.close_edit()

        reply=QMessageBox()
        reply.setWindowTitle('提示')
        reply.setText('是否将本次操作写入磁盘？')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Ignore)
        buttonY = reply.button(QMessageBox.Yes)
        buttonY.setText('是')
        buttonN = reply.button(QMessageBox.No)
        buttonN.setText('取消')
        buttonI=reply.button(QMessageBox.Ignore)
        buttonI.setText('否')

        reply.exec_()

        if reply.clickedButton()==buttonI:
            event.accept()
        elif reply.clickedButton()==buttonY:
            self.saveFile()#如果用户选择是，则调用保存文件的函数
            event.accept()
        else:
            event.ignore()


if __name__=='__main__':
    app=QApplication(sys.argv)

    mainform=mainForm()

    mainform.show()

    sys.exit(app.exec_())

