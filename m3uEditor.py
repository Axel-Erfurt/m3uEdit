#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import pandas as pd
from PyQt5.QtCore import Qt, QDir, QAbstractTableModel, QModelIndex, QVariant, QSize, QProcess
from PyQt5.QtWidgets import (QMainWindow, QTableView, QApplication, QLineEdit, QComboBox, QWidget, 
                             QFileDialog, QAbstractItemView, QMessageBox, QToolButton, QToolBar, QSizePolicy)
from PyQt5.QtGui import QStandardItem, QIcon, QKeySequence

class PandasModel(QAbstractTableModel):
    def __init__(self, df = pd.DataFrame(), parent=None): 
        QAbstractTableModel.__init__(self, parent=None)
        self._df = df
        self.setChanged = False
        self.dataChanged.connect(self.setModified)

    def setModified(self):
        self.setChanged = True

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError, ):
                return QVariant()
        elif orientation == Qt.Vertical:
            try:
                return self._df.index.tolist()[section]
            except (IndexError, ):
                return QVariant()

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if (role == Qt.EditRole):
                return self._df.values[index.row()][index.column()]
            elif (role == Qt.DisplayRole):
                return self._df.values[index.row()][index.column()]
        return None

    def setData(self, index, value, role):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        self._df.values[row][col] = value
        self.dataChanged.emit(index, index)
        return True

    def rowCount(self, parent=QModelIndex()): 
        return len(self._df.index)

    def columnCount(self, parent=QModelIndex()): 
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(colname, ascending= order == Qt.AscendingOrder, inplace=True)
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()

class Viewer(QMainWindow):
    def __init__(self, parent=None):
      super(Viewer, self).__init__(parent)
      self.df = None
      self.filename = ""
      self.fname = ""
      self.csv_file = ""
      self.m3u_file = ""
      self.process = QProcess()
      self.setGeometry(0, 0, 1000, 600)
      self.lb = QTableView()
      self.lb.horizontalHeader().hide()
      self.model =  PandasModel()
      self.lb.setModel(self.model)
      self.lb.setEditTriggers(QAbstractItemView.DoubleClicked)
      self.lb.setSelectionBehavior(self.lb.SelectRows)
      self.lb.setSelectionMode(self.lb.SingleSelection)
      self.lb.setDragDropMode(self.lb.InternalMove)
      self.setStyleSheet(stylesheet(self))
      self.lb.setAcceptDrops(True)
      self.setCentralWidget(self.lb)
      self.setContentsMargins(10, 10, 10, 10)
      self.statusBar().showMessage("Ready", 0)
      self.setWindowTitle("m3u Editor")
      self.setWindowIcon(QIcon.fromTheme("multimedia-playlist"))
      self.createToolBar()
      self.lb.setFocus()
      
    def copy_row(self):
        if self.model.rowCount() < 1:
            return
        i = self.lb.selectionModel().selection().indexes()[0].row()
        b = self.df.iloc[i].copy()
        name = b[0]
        group = b[1]
        logo = b[2]
        id = b[3]
        url = b[4]
        self.copied_row = b
        c_line = f'#EXTINF:-1 tvg-name="{name}" group-title="{group}" tvg-logo="{logo}" tvg-id="{id}"\n{url}'
        QApplication.clipboard().setText(c_line)
        
    def cut_row(self):
        if self.model.rowCount() < 1:
            return
        i = self.lb.selectionModel().selection().indexes()[0].row()
        self.copy_row()
        self.del_row()
        self.model.setChanged = True
        
    def paste_row(self):
        if self.model.rowCount() < 1:
            return
        i = self.lb.selectionModel().selection().indexes()[0].row()
        self.df.iloc[i] = self.copied_row
        self.model.setChanged = True
  
    def convert_to_csv(self):
        mylist = open(self.m3u_file, 'r').read().splitlines()

        headers = ['tvg-name', 'group-title', 'tvg-logo', 'tvg-id', 'url']
        group = ""
        ch = ""
        url = ""
        id = ""
        logo = ""
        csv_content = ""
        csv_content += '\t'.join(headers)
        csv_content += "\n"
        for x in range(1, len(mylist)-1):
            line = mylist[x]
            nextline = mylist[x+1]
            if line.startswith("#EXTINF") and not "**********" in line:
                if 'tvg-name="' in line:
                    ch = line.partition('tvg-name="')[2].partition('"')[0]
                elif 'tvg-name=' in line:
                    ch = line.partition('tvg-name=')[2].partition(' tvg')[0]
                else:
                    ch = line.rpartition(',')[2]        
                if ch == "":
                    ch = "No Name"
                ch = ch.replace('"', '')
                    
                if 'group-title="' in line:
                    group = line.partition('group-title="')[2].partition('"')[0]

                elif "group-title=" in line:
                    group = line.partition('group-title=')[2].partition(' tvg')[0]
                else:
                    group = "TV"
                group = group.replace('"', '')        
                
                if 'tvg-id="' in line:
                    id = line.partition('tvg-id="')[2].partition('"')[0]
                elif 'tvg-id=' in line:
                    id = line.partition('tvg-id=')[2].partition(' ')[0]
                else:
                    id = ""
                id = id.replace('"', '')
                
                url = nextline
                if 'tvg-logo="' in line:
                    logo = line.partition('tvg-logo="')[2].partition('"')[0]
                elif 'tvg-logo=' in line:
                    logo = line.partition('tvg-logo=')[2].partition(' ')[0]        
                else:
                    logo = ""            
                csv_content += (f'{ch}\t{group}\t{logo}\t{id}\t{url}\n')
        self.fname = self.m3u_file.rpartition("/")[2].replace(".m3u", ".csv")
        self.csv_file = f'/tmp/{self.fname}'
        with open(self.csv_file, 'w') as f:        
            f.write(csv_content)

    def closeEvent(self, event):
        print(self.model.setChanged)
        if  self.model.setChanged == True:
            quit_msg = "<b>The document was changed.<br>Do you want to save the changes?</ b>"
            reply = QMessageBox.question(self, 'Save Confirmation', 
                     quit_msg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                event.accept()
                self.writeCSV()
        else:
            print("nothing changed. goodbye")

    def createToolBar(self):
        tb = QToolBar("Tools")
        tb.setMovable(False)
        tb.setAllowedAreas(Qt.TopToolBarArea)
        self.addToolBar(tb)
        tb.setIconSize(QSize(16, 16))

        new_btn = QToolButton()
        new_btn.setShortcut(QKeySequence.New)
        new_btn.setIcon(QIcon.fromTheme("document-new"))
        new_btn.setToolTip("create new m3u File")
        new_btn.clicked.connect(self.new_file)
        tb.addWidget(new_btn)
        
        open_btn = QToolButton()
        open_btn.setShortcut(QKeySequence.Open)
        open_btn.setIcon(QIcon.fromTheme("document-open"))
        open_btn.setToolTip("open m3u File")
        open_btn.clicked.connect(self.loadM3U)
        tb.addWidget(open_btn)

        save_btn = QToolButton()
        save_btn.setShortcut(QKeySequence.SaveAs)
        save_btn.setIcon(QIcon.fromTheme("document-save"))
        save_btn.setToolTip("save m3u File")
        save_btn.clicked.connect(self.writeCSV)
        tb.addWidget(save_btn)
        
        empty = QWidget()
        empty.setFixedWidth(44)
        tb.addWidget(empty)

        cut_btn = QToolButton()
        cut_btn.setIcon(QIcon.fromTheme("edit-cut"))
        cut_btn.setToolTip("cut row")
        cut_btn.clicked.connect(self.cut_row)
        tb.addWidget(cut_btn)
        
        copy_btn = QToolButton()
        copy_btn.setIcon(QIcon.fromTheme("edit-copy"))
        copy_btn.setToolTip("copy row")
        copy_btn.clicked.connect(self.copy_row)
        tb.addWidget(copy_btn)

        paste_btn = QToolButton()
        paste_btn.setIcon(QIcon.fromTheme("edit-paste"))
        paste_btn.setToolTip("paste row")
        paste_btn.clicked.connect(self.paste_row)
        tb.addWidget(paste_btn)

        next_empty = QWidget()
        next_empty.setFixedWidth(44)        
        tb.addWidget(next_empty)
        
        del_btn = QToolButton()
        del_btn.setIcon(QIcon.fromTheme("edit-delete"))
        del_btn.setToolTip("delete row")
        del_btn.clicked.connect(self.del_row)
        tb.addWidget(del_btn)
        
        add_btn = QToolButton()
        add_btn.setIcon(QIcon.fromTheme("add"))
        add_btn.setToolTip("add row")
        add_btn.clicked.connect(self.add_row)
        tb.addWidget(add_btn)

        move_down_btn = QToolButton()
        move_down_btn.setIcon(QIcon.fromTheme("down"))
        move_down_btn.setToolTip("move down")
        move_down_btn.clicked.connect(self.move_down)
        tb.addWidget(move_down_btn)
        
        move_up_up = QToolButton()
        move_up_up.setIcon(QIcon.fromTheme("up"))
        move_up_up.setToolTip("move up")
        move_up_up.clicked.connect(self.move_up)
        tb.addWidget(move_up_up)
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        tb.addWidget(spacer)
        
        self.filter_field = QLineEdit(placeholderText = "filter group (press Enter)")
        self.filter_field.setClearButtonEnabled(True)
        self.filter_field.setToolTip("insert search term and press enter\n use Selector → to choose column for filter")
        self.filter_field.setFixedWidth(200)
        self.filter_field.returnPressed.connect(self.filter_table)
        self.filter_field.textChanged.connect(self.update_filter)
        tb.addWidget(self.filter_field)
        
        self.filter_combo = QComboBox()
        self.filter_combo.setToolTip("choose column for filter")
        self.filter_combo.setFixedWidth(100)
        self.filter_combo.addItems(['tvg-name', 'group-title', 'tvg-logo', 'tvg-id', 'url'])
        self.filter_combo.currentIndexChanged.connect(self.filter_table)
        tb.addWidget(self.filter_combo)
        
        play_btn = QToolButton()
        play_btn.setIcon(QIcon.fromTheme("mpv"))
        play_btn.setToolTip("play with mpv")
        play_btn.clicked.connect(self.play_with_mpv)
        tb.addWidget(play_btn)
        
        stop_btn = QToolButton()
        stop_btn.setIcon(QIcon.fromTheme("media-playback-stop"))
        stop_btn.setToolTip("stop mpv")
        stop_btn.clicked.connect(self.stop_mpv)
        tb.addWidget(stop_btn)
        
        self.addToolBarBreak()
        
        tbf = QToolBar("Find")
        tbf.setMovable(False)
        tbf.setAllowedAreas(Qt.TopToolBarArea)
        self.addToolBar(tbf)
        self.findfield = QLineEdit(placeholderText = "find ...")
        self.findfield.setClearButtonEnabled(True)
        self.findfield.setFixedWidth(200)
        tbf.addWidget(self.findfield)
        
        tbf.addSeparator()
        
        self.replacefield = QLineEdit(placeholderText = "replace with ...")
        self.replacefield.setClearButtonEnabled(True)
        self.replacefield.setFixedWidth(200)
        tbf.addWidget(self.replacefield)
        
        btn = QToolButton()
        btn.setText("replace all in  →")
        btn.setToolTip("replace all\n select column for replacing  →")
        btn.clicked.connect(self.replace_in_table)
        tbf.addWidget(btn)
        
        self.replace_filter_combo = QComboBox()
        self.replace_filter_combo.setToolTip("choose column for filter")
        self.replace_filter_combo.setFixedWidth(160)
        self.replace_filter_combo.addItems(['tvg-name', 'group-title', 'tvg-name + group-title'])
        tbf.addWidget(self.replace_filter_combo)
        
    def new_file(self):
        columns = ["name", "group", "logo", "id", "url"]
        self.df = pd.DataFrame(columns=["name", "group", "logo", "id", "url"])
        self.df.loc[len(self.df)] = columns
        self.model = PandasModel(self.df)
        self.lb.setModel(self.model)
        self.lb.selectRow(self.model.rowCount() - 1)
        self.model.setChanged = True
        
        
    def play_with_mpv(self):
        if self.model.rowCount() < 1:
            return
        i = self.lb.selectionModel().selection().indexes()[0].row()
        url = self.df.iloc[i][4]
        print(i, url)
        self.process.start("mpv", ['--geometry=33%', url])
            
    def stop_mpv(self):
        if self.model.rowCount() < 1:
            return
        self.process.kill()
        
    def move_down(self):
        if self.model.rowCount() < 1:
            return
        i = self.lb.selectionModel().selection().indexes()[0].row()
        b, c = self.df.iloc[i].copy(), self.df.iloc[i+1].copy()
        self.df.iloc[i],self.df.iloc[i+1] = c,b
        self.model.setChanged = True
        self.lb.selectRow(i+1)
        
    def move_up(self):
        if self.model.rowCount() < 1:
            return
        i = self.lb.selectionModel().selection().indexes()[0].row()
        b, c = self.df.iloc[i].copy(), self.df.iloc[i-1].copy()
        self.df.iloc[i],self.df.iloc[i-1] = c,b
        self.model.setChanged = True
        self.lb.selectRow(i-1)
        
    def del_row(self): 
        if self.model.rowCount() < 1:
            return
        i = self.lb.selectionModel().selection().indexes()[0].row()
        if len(self.df.index) > 0:
            self.df = self.df.drop(self.df.index[i])
            self.model = PandasModel(self.df)
            self.lb.setModel(self.model)
            self.model.setChanged = True
            self.lb.selectRow(i)
            
    def add_row(self): 
        if self.model.rowCount() > 0:
            i = self.lb.selectionModel().selection().indexes()[0].row()
            print("adding row")
            newrow = {0:'name', 1:'title', 2:'logo', 3:'id', 4:'url'}       
            self.df = self.df.append(newrow, ignore_index=True)
            self.model = PandasModel(self.df)
            self.lb.setModel(self.model)
            self.model.setChanged = True
            self.lb.selectRow(self.model.rowCount() - 1)
                
    def openFile(self, path=None):
        if  self.model.setChanged == True:
            quit_msg = "<b>The document was changed.<br>Do you want to save the changes?</ b>"
            reply = QMessageBox.question(self, 'Save Confirmation', 
                     quit_msg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                path, _ = QFileDialog.getOpenFileName(self, "Open File", QDir.homePath() + "/Dokumente/TV/","Playlists (*.m3u)")
                if path:
                    return path
        else:
            path, _ = QFileDialog.getOpenFileName(self, "Open File", QDir.homePath() + "/Dokumente/TV/","Playlists (*.m3u)")
            if path:
                return path            

    def loadM3U(self):
        if self.model.setChanged == True:
            save_msg = "<b>The document was changed.<br>Do you want to save the changes?</ b>"
            reply = QMessageBox.question(self, 'Save Confirmation', 
                     save_msg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.writeCSV()
                self.open_m3u()
            else:
                self.model.setChanged = False
                self.open_m3u()
        else:
            self.model.setChanged = False
            self.open_m3u()
        
    def open_m3u(self):
        fileName = self.openFile()
        if fileName:
            self.m3u_file = fileName
            self.convert_to_csv()
            print(fileName + " loaded")
            f = open(self.csv_file, 'r+b')
            with f:
                self.filename = fileName
                self.df = pd.read_csv(f, delimiter = '\t', keep_default_na = False, low_memory=False, header=None)
                self.model = PandasModel(self.df)
                self.lb.setModel(self.model)
                self.lb.resizeColumnsToContents()
                self.lb.selectRow(0)
                self.statusBar().showMessage(f"{fileName} loaded", 0)
                self.model.setChanged = False
                self.lb.verticalHeader().setMinimumWidth(24)
             

    def writeCSV(self):
        if self.model.rowCount() < 1:
            return
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File", self.fname.replace(".csv", ".m3u"),"M3U Files (*.m3u)")
        if fileName:
            # save temporary csv
            f = open(self.csv_file, 'w')
            newModel = self.model
            dataFrame = newModel._df.copy()
            dataFrame.to_csv(f, sep='\t', index = False, header = False)  
            f.close()
            
            # convert to m3u
            mylist = open(self.csv_file, 'r').read().splitlines()
            group = ""
            ch = ""
            url = ""
            id = ""
            logo = ""
            m3u_content = ""

            headers = ['tvg-name', 'group-title', 'tvg-logo', 'tvg-id', 'url']
            m3u_content += "#EXTM3U\n"

            for x in range(1, len(mylist)):
                line = mylist[x].split('\t')
                ch = line[0]
                group = line[1]
                logo = line[2]
                id = line[3]
                url = line[4]
                
                m3u_content += f'#EXTINF:-1 tvg-name="{ch}" group-title="{group}" tvg-logo="{logo}" tvg-id="{id}",{ch}\n{url}\n'

            with open(fileName, 'w') as f:        
                f.write(m3u_content)

            print(fileName + " saved")
            self.model.setChanged = False


    def replace_in_table(self):
        if self.model.rowCount() < 1:
            return
        index = self.replace_filter_combo.currentIndex()
        searchterm = self.findfield.text()
        replaceterm = self.replacefield.text()
        if searchterm == "" or replaceterm == "":
            return
        else:
            if len(self.df.index) > 0:
                if index == 0 or index == 1:
                    self.df[index].replace(searchterm, replaceterm, inplace=True, regex=True)
                else:
                    self.df[0].replace(searchterm, replaceterm, inplace=True, regex=True)
                    self.df[1].replace(searchterm, replaceterm, inplace=True, regex=True)
            self.lb.resizeColumnsToContents()       
            self.model.setChanged = True
                
    def filter_table(self):
        if self.model.rowCount() < 1:
            return
        self.clear_filter()
        index = self.filter_combo.currentIndex()
        searchterm = self.filter_field.text()  
        if searchterm == "":
            return
        row_list = []
        self.lb.clearSelection()

        for i in range(self.lb.model().columnCount()):
            indexes = self.lb.model().match(
                                self.lb.model().index(0, index),
                                Qt.DisplayRole,
                                searchterm,
                                -1,
                                Qt.MatchContains
                            )
            for ix in indexes:
                self.lb.selectRow(ix.row())    
                row_list.append(ix.row()) 
                
        for x in range(self.lb.model().rowCount()):
            if not x in row_list:
                self.lb.hideRow(x)
       
    def update_filter(self):
        if self.filter_field.text() == "":
            self.clear_filter()

    def clear_filter(self):
        for x in range(self.lb.model().rowCount()):
            self.lb.showRow(x)        
            
def stylesheet(self):
        return """
    QTableView
        {
            border: 1px solid #d3d7cf;
            border-radius: 0px;
            font-size: 8pt;
            background: #eeeeec;
            selection-color: #ffffff
        }
    QTableView::item:hover
        {   
            color: black;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #729fcf, stop:1 #d3d7cf);           
        }
        
    QTableView::item:selected {
            color: #F4F4F4;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #6169e1, stop:1 #3465a4);
        } 

    QTableView QTableCornerButton::section {
            background: #D6D1D1;
            border: 0px outset black;
        }
        
    QHeaderView:section {
            background: #d3d7cf;
            color: #555753;
            font-size: 8pt;
        }
        
    QHeaderView:section:checked {
            background: #204a87;
            color: #ffffff;
        }
        
    QStatusBar
        {
        font-size: 7pt;
        color: #555753;
        }
    QToolButton:hover
        {   
            background: #a5dcff;           
        }        
    """
 
if __name__ == "__main__":
 
    app = QApplication(sys.argv)
    main = Viewer()
    main.show()
sys.exit(app.exec_())
