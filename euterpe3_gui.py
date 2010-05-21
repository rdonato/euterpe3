import sys
import sys
import os
import string
import locale
import gobject
import dbus
import dbus.service
import time
import pycurl
import StringIO
import thread
from array import array
from dbus.mainloop.glib import DBusGMainLoop
from PyQt4 import QtGui,QtCore

reload(sys)
sys.setdefaultencoding(locale.getdefaultlocale()[1])

class EuterpeGui(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ctimer = QtCore.QTimer()
        widge = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        self.ok = True
        self.setGeometry(400, 300, 400, 250)
        self.setWindowTitle('Euterpe release 3.0')
        self.statusBar().showMessage('Riccardo Donato info@: http://www.rdonato.net')
        self.center()
        self.setWindowIcon(QtGui.QIcon('web.png'))
        self.setToolTip('Press Start! to send tracks to your <b>skype</b>')
        QtGui.QToolTip.setFont(QtGui.QFont('OldEnglish', 10))
        self.button_layout = QtGui.QHBoxLayout()
        self.lineEdit = QtGui.QLineEdit(self)
        pic = QtGui.QLabel(self)
        pic.setGeometry(300, 10, 90, 90)
        pic.setPixmap(QtGui.QPixmap(os.getcwd() + "/web.png"))
        self.label = QtGui.QLabel(self)
        self.label2 = QtGui.QLabel(self)
        self.label3 = QtGui.QLabel(self)
        self.label2.setGeometry(QtCore.QRect(20, 30, 90, 24))
        self.label3.setGeometry(QtCore.QRect(20, 30, 350, 124))
        self.label3.setText(unicode('Press start to begin!'))
        self.label2.setText(unicode('Username: '))
        self.label2.show()
        self.lineEdit.setGeometry(QtCore.QRect(95, 30, 150, 24))
        self.label.setGeometry(QtCore.QRect(95, 30, 200, 24))
        self.label.hide()
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setMaxLength(20)
        self.lineEdit.setText(unicode('cuciniere_zen'))        
        self.startButton = QtGui.QPushButton("&Start")
        self.stopButton = QtGui.QPushButton("&Change Username")
        self.startButton.clicked.connect(self.startDirectThread)
        self.stopButton.clicked.connect(self.startDirectThread)
        QtCore.QObject.connect(self.ctimer, QtCore.SIGNAL("timeout()"), self.showSong)
        self.proc = ConnectedThread()
        self.proc.start()
        self.button_layout.addWidget(self.startButton) 
        self.button_layout.addWidget(self.stopButton)
        self.stopButton.hide()
        layout.addWidget(self.label)
        layout.addLayout(self.button_layout)
        widge.setLayout(layout)
        self.setCentralWidget(widge)
        
        
    @QtCore.pyqtSlot()
    def startDirectThread(self):
        if self.ok:
            self.ok = False
            self.x = DirectThread()
            self.x.start()
            global user,flagMood 
            user = str(self.lineEdit.text())
            print "DEBUG Username:", user
            self.x.finished.connect(self.xFinished)
            
    @QtCore.pyqtSlot()
    def sleepNoThread(self):
        print QtCore.QThread.currentThreadId()
        #QtCore.QThread.sleep(1)
        
    @QtCore.pyqtSlot()
    def xFinished(self):
        print "DEBUG ", QtCore.QThread.currentThreadId()
        #self.startButton.setText('Started!')
        self.startButton.hide()
        self.stopButton.show()
        self.lineEdit.setFocus()
        self.ctimer.start(1000)
        #self.button_layout.removeWidget(self.startButton)
        #self.button_layout.setEnabled(False)
        self.ok = True
        
    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)  
    
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes: 
            mood = "SET PROFILE MOOD_TEXT Legge di Truman: Se non li puoi convincere, confondili."
            skype.Send(mood)           
            event.accept()
        else:
            event.ignore()      
     
    def showSong(self):
        if flagMood :
            self.label3.setText(unicode('Sending: '+song))
        else   :
            self.label3.setText(unicode('Your player is paused!!')) 
        
        
class DirectThread(QtCore.QThread):
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self,parent)
    def run(self):
        print "DEBUG ", QtCore.QThread.currentThreadId()

        
class ConnectedThread(QtCore.QThread):
    
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self,parent)
        
    def run(self):
        print "Thread number: ",QtCore.QThread.currentThreadId()
        self.exec_()
        
    @QtCore.pyqtSlot()
    def stopNWait(self):
        print "DEBUG ", QtCore.QThread.currentThreadId()
        mood = "SET PROFILE MOOD_TEXT Legge di Truman: Se non li puoi convincere, confondili."
        print "DEBUG mood ", mood
        flagMood = False
        skype.Send(mood)
        
    def readyOK(self):
        global user,flagMood
        flagMood = False   

class Callback_obj(dbus.service.Object):
    def __init__(self, bus, object_path, out):
        self.out = out
        dbus.service.Object.__init__(self, bus, object_path, bus_name='com.Skype.API')

    @dbus.service.method(dbus_interface='com.Skype.API')
    def Notify(self, message_text):
        print ('received:', message_text)
        args = message_text.split(None)
        if args[0] == 'CALL':
            call_id = args[1]
            #print "Call ID = ", call_id
            if args[2] == 'STATUS':
                if args[3] == 'RINGING':
                    msg = 'ALTER CALL '+call_id+' ANSWER'
                    self.Send(msg)
                    print ('Test message')

    def Send(self, message_text):
        print ("sending:", message_text)
        resp = self.out.Invoke(message_text)
        print ("answer: ", resp)
        return resp

def checkPid(progname):
    pidRawNumber = os.popen( "pidof %s "%progname ).readlines()
    pid = []
    try: 
      for line in pidRawNumber:
        pid.append(int(string.split(line)[0]))
      return True if pid[0]>0 else False #operatore ternario in python!
    except IndexError:
      return False

def getCpuLoad():
    cpuLoad=os.popen("ps aux|awk 'NR > 0 { s +=$3 }; END {print \"cpu %\",s}'").readlines()
    return cpuLoad[0]

def startSkype():
    print ("Checking Skype status...")    
    if checkPid("skype"):
        print "Skype is running"
    else:    
        os.system("skype")        

def mainProg():
        global song,flagMood,  skype, remote_bus, out_connection
        try:
            thread.start_new_thread( startSkype,() )
        except KeyboardInterrupt:
            print "Euterpe terminates...."
        time.sleep(5)
        DBusGMainLoop(set_as_default=True)
        loop = gobject.MainLoop()
        remote_bus = dbus.SessionBus()
        try:
            out_connection = remote_bus.get_object('com.Skype.API', '/com/Skype')
        except dbus.exceptions.DBusException:
            print "Skype closed...bye bye!"
            sys.exit(0)   
        skype = Callback_obj(remote_bus, '/com/Skype/Client', out_connection)
        skype.Send('NAME Euterpe')
        skype.Send('PROTOCOL 5')
        while (True):
         now = int(time.time())
         rawsong = StringIO.StringIO()
         c = pycurl.Curl()
         while (user == "null"):
            pass
         def getUser():
            link = "http://ws.audioscrobbler.com/1.0/user/"+user+"/recenttracks.txt"
            return link
         c.setopt(c.URL, getUser())
         c.setopt(pycurl.WRITEFUNCTION, rawsong.write)
         c.perform()
         song_time = rawsong.getvalue().split('\n')[0].split(',')[0]
         song = rawsong.getvalue().split('\n')[0].split(',')[1]
         print "DEBUG song ", song
         diff=now- int(song_time)
         if diff > 600:
            flagMood = False 
            message = "SET PROFILE MOOD_TEXT Legge di Truman: Se non li puoi convincere, confondili. "+time.asctime( time.localtime(time.time()) )
         else :
            message = "SET PROFILE MOOD_TEXT (music)"+song[0:(len(song)-0)]+" http://code.google.com/p/euterpe3/"
            flagMood = True
         new_message = unicode(message,"UTF-8")
         #if flagMood: new_message=mood
         try:
            skype.Send(new_message.encode())
         except :
            print "Skype closed...bye bye!"  
            sys.exit(0)
         time.sleep(90)
        loop.run()


flagMood = False
user = "null"
if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    wid = EuterpeGui()
    wid.show()
    thread.start_new_thread( mainProg,() ) 
    sys.exit(app.exec_())   
