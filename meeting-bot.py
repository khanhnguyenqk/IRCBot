#!/usr/bin/env python
import socket
import random
import string

class IRCConnecting:
    def __init__(self):
        self.settingDictionary = self.readConfigFile()

    def test(self):
        for key in self.settingDictionary.keys():
            print ("%s = %s" % (key, self.settingDictionary[key]))

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

    def connect(self):
        self.irc.connect((self.settingDictionary["server"], int(self.settingDictionary["port"])))

    def login(self, nickname, username='username', realname='realname', hostname='hostname', servername='servername'):
        self.sendData("USER %s %s %s %s" % (username, hostname, servername, realname))
        self.sendData("NICK " + nickname)

    def sendData(self, command):
        self.irc.send(command + '\n')

    def join(self, channel):
        self.sendData("JOIN %s" % channel)

    def stayConnected(self):
        while (1):
            buffer = self.irc.recv(1024)
            print "Server says: %s" % buffer
            msg = string.split(buffer)
            if msg[0] == "PING":
                self.sendData("PONG %s" % msg[1])
            if msg[0] == ".quit":
                self.sendData("QUIT")

class IRCMeeting(IRCConnecting):
    def __init__(self):
        None

if __name__ == '__main__':
    mb = IRCConnecting()
    mb.initiateConnection()
    mb.connect()
    mb.login(mb.settingDictionary['nick'])
    mb.join(mb.settingDictionary['channel'])
    mb.stayConnected()
