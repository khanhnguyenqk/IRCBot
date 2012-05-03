#!/usr/bin/env python
import socket
import random
import string
import os
import sys
import time

from multiprocessing import Process, Value

class IRCConnecting:
    def __init__(self):
        self.settingDictionary = self.readConfigFile()
        # 0: initiated
        #1: connecting in side loop 
        #2: ask to be disconnected
        #3: disconnected
        #4: running extra feature
        self.status = Value('i',0) 

    def readConfigFile(self, filePath='meeting-botrc'):
        f = open(filePath)
        lines = f.readlines()
        # Line format: key=value\n. Extract key / value put to dictionary
        dictionary = {}
        for line in lines:
            l = line[:-1]
            key = l[:string.find(l, '=')]
            value = l[string.find(l, '=') + 1:]
            dictionary[key]=value
        return dictionary 

    def initiateConnection(self):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connectServer(self):
        self.irc.connect((self.settingDictionary["server"], int(self.settingDictionary["port"])))

    def login(self, nickname, username='username', realname='realname', \
        hostname='hostname', servername='servername'):
        self.sendData("USER %s %s %s %s" % (username, hostname, servername, realname))
        self.sendData("NICK " + nickname)

    def sendData(self, command):
        self.irc.send(command + '\n')

    def sendPrivMessage(self, msg):
        self.sendData("PRIVMSG %s :%s" % (self.settingDictionary["channel"], msg))

    def join(self, channel):
        self.sendData("JOIN %s" % channel)

    def run(self):
        """Do connect server, login, join room, stay connected"""
        self.initiateConnection()
        self.connectServer()
        self.login(mb.settingDictionary['nick'])
        self.join(mb.settingDictionary['channel'])
        p = Process(target=self.forkStayConnected, args=(self.status, ))
        p.start()

        self.startDoingExtra()
        while self.status.value == 4:
            self.doExtra()
        p.join()

    def forkStayConnected(self, status):
        status.value = 1
        while (1):
            buffer = self.irc.recv(1024)
            msg = string.split(buffer)
            print "Server says: %s" % buffer
            if msg[-1] == ":.quit":
                if status.value != 1:
                    self.sendPrivMessage("Can't disconnect. Check if I'm doing something.")
                elif status.value == 1:
                    self.sendData("Bye!")
                    status.value = 3
                    self.irc.close()
                    sys.exit() 
            if msg[0] == "PING":
                self.sendData("PONG %s" % msg[1])

    def disconnect(self):
        if self.status.value == 1:
            self.status.value = 2
        while 1:
            if self.status.value == 3:
                self.irc.close()
                break

    def doExtra(self):
        """Abstract Method. Put what you want to do here. Always call stopDoingExtra at the end"""
        None

    def startDoingExtra(self):
        while self.status.value != 1:
            time.sleep(1)
        self.status.value = 4

    def stopDoingExtra(self):
        if self.status.value == 4:
            self.status.value = 1

class IRCMeeting(IRCConnecting):
    def doExtra(self):
        while self.status.value == 4:
            print "------------------------"
            print "Doing extra"
            print "------------------------"

            buffer = self.irc.recv(1024)
            msg = string.split(buffer)
            
            if msg[-1] == ":.end":
                print "------------------------"
                print "Ending extra loop"
                print "------------------------"
                self.stopDoingExtra()
                break
            if msg[-1] == ":.names":
                self.sendData("NAMES")
            else:
                self.sendPrivMessage("You said: %s" % msg[-1])

if __name__ == '__main__':
    mb = IRCMeeting()
    mb.run()
