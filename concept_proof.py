#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import sys
import json
import time
import os
import subprocess
import threading
from random import randint


path_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(path_root + "/network/snmpd/")


def receive_signal(signum, stack):
    print '-------->Received: %d' % signum
    print '-------->stack: %s' % stack
    sys.exit(0)


def wifi_link():
    game = randint(0, 10)
    if game > 3:
        string = """
            SSID: dlink-aeluin
            freq: 2412
            RX: 371176 bytes (2674 packets)
            TX: 869 bytes (16 packets)
            signal: -18 dBm
            tx bitrate: 78.0 MBit/s MCS 12"""
    else:
        string = "Not connected."
    return string


def gen_default_program():
    with open('/home/user_program/default.sh', 'a') as file:
        file.write("#!/bin/sh\n")
        file.write("while [ 1 ];\n")
        file.write("do\n")
        file.write("    sleep 3600\n")
        file.write("done\n")


def gen_db_file():
    #return os.system("ping 8.8.8.9 -c 2 -w 5 &> /dev/null")
    cmd = "ping 8.8.8.9 -c 1 -w 2"

    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    result = process.communicate()[0]
    return result.find("0 received")


global_table = list()
message_mutex = threading.Lock()
semaphore = threading.Semaphore(1)


class mainThread:
    def __init__(self):
        self.a_thread = aThread()
        self.a_thread.daemon = True
        self.a_thread.start()

        self.b_thread = bThread()
        self.b_thread.daemon = True
        self.b_thread.start()

        t = threading.Thread(target=self.myThread)
        t.daemon = True
        t.start()

        while True:
            time.sleep(60)

    def myThread(self):
        global global_table
        while True:
            print global_table
            time.sleep(1)


class bThread(threading.Thread):
    # ping_list = [["8.8.8.8", 1], ["8.8.4.4", 3], ["8.8.8.9", 3]]
    def __init__(self):
        super(bThread, self).__init__()
        self.stoprequest = threading.Event()

    def run(self):
        global global_table
        global message_mutex
        global semaphore
        while not self.stoprequest.isSet():
            message_mutex.acquire()
            global_table = list()
            global_table.append("B")
            time.sleep(30)
            message_mutex.release()
            time.sleep(1)

    def join(self, timeout=None):
        self.stoprequest.set()
        super(bThread, self).join(timeout)


# Function
def remove_dup_process(keyword, delete_pid):
    ps = subprocess.Popen(
        ['ps', 'aux'], stdout=subprocess.PIPE).communicate()[0]
    processes = ps.split('\n')
    nfields = len(processes[0].split()) - 1
    split_list = list()
    dead_pid_list = list()
    for row in processes[1:]:
        split_list.append(row.split(None, nfields))

    for row in split_list:
        for item in row:
            if item.find(keyword) != -1:
                #print row
                dead_pid_list.append(row[1])

    print "before dead_pid_list: %s" % dead_pid_list
    cmd = "kill %s" % delete_pid
    print "cmd: %s" % cmd
    #subprocess.call(cmd, shell=True)

    try:
        print "remove delete_pid: %s" % delete_pid
        dead_pid_list.remove(str(delete_pid))

    except Exception as e:
        print "error when remove pid, %s", e
        pass

    if len(dead_pid_list) == 1:
        return int(dead_pid_list[0])
    else:
        print "-------> error on dead_pid_list"
        return False


def shorewall_recover_system():
    shorewall_status_string = subprocess.Popen(
        ["shorewall", "status"], stdout=subprocess.PIPE).communicate()[0]
    if shorewall_status_string.find("is stopped") == -1:
        # shorewall UP
        subprocess.call("shorewall save", shell=True)
    else:
        # shorewall DOWN
        subprocess.call("shorewall restore", shell=True)


def check_ps(name):
    cmd = "ps aux | grep %s | grep -v grep" % name
    out = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]
    if out != "":
        return True
    else:
        return False


class aThread(threading.Thread):
    def __init__(self):
        super(aThread, self).__init__()
        self.stoprequest = threading.Event()

    def run(self):
        return 0
        while not self.stoprequest.isSet():
            i = 0
            while i < 10:
                print "a"
                i += 1
                time.sleep(1)
                #exit(0)

    def join(self, timeout=None):
        self.stoprequest.set()
        print "kill a start"
        super(aThread, self).join(timeout)
        print "kill a end"


class cThread(threading.Thread):
    def __init__(self):
        super(cThread, self).__init__()
        self.stoprequest = threading.Event()

    def run(self):
        return 0
        while not self.stoprequest.isSet():
            while True:
                print "c"
                time.sleep(1)

    def join(self, timeout=None):
        self.stoprequest.set()
        print "kill c start"
        super(aThread, self).join(timeout)
        print "kill c end"


class ThreadManager(threading.Thread):
    def __init__(self):
        super(ThreadManager, self).__init__()
        self.stoprequest = threading.Event()

    def run(self):
        a = aThread()
        a.daemon = True
        a.start()

        c = cThread()
        c.daemon = True
        c.start()
        while not self.stoprequest.isSet():

            print a.isAlive()
            time.sleep(1)
            a.join()
            print a.isAlive()

    def join(self, timeout=None):
        self.stoprequest.set()
        super(aThread, self).join(timeout)


def devide_by_8(value):
    try:
        value = int(value)
    except Exception:
        return None

    value = value / 8
    return value

    if value <= 0:
        return 1

#--------------------------------- FTP ------------------------------------
from ftplib import FTP


class FtpClient:
    def __init__(self, ip, port, username, password):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        time.sleep(30)

    def download(self, remote_filename, local_filename):
        try:
            ftp = FTP(self.ip, timeout=5)
        except Exception:
            print "FTP Connect Failed..."
            return False
        else:
            print "FTP connect OK"

        try:
            ftp.login(self.username, self.password)
        except Exception:
            print "FTP login failed"
            ftp.quit()
        else:
            ftp.retrlines('LIST')

        try:
            ftp.retrbinary(
                'RETR %s' % remote_filename, open(local_filename, 'wb').write)
        except Exception:
            print 'ERROR: cannot read file "%s"' % remote_filename
            os.unlink(local_filename)   # remove the file
        else:
            print '*** Downloaded "%s" to CWD' % local_filename

        ftp.quit()

    def __del__(self):
        print "exit!"


def get_cellular_signal(interface_id):
    signal = 99
    try:
        db = open("cellularinfo")
        cellular_signal_info = json.load(db)
        db.close()

        for obj in cellular_signal_info:
            if obj['id'] == interface_id:
                signal = obj['signal']
                break
    except Exception:
        pass

    return signal


from datetime import datetime


def time_duration():
    a = datetime.now()
    b = datetime.now()
    c = b - a
    return divmod(c.days * 86400 + c.seconds, 60)[0]


def get_providers_line():
    print "------------------------------------------->"
    result = list()
    f = open('route.list', 'r')
    for line in f.readlines():
        line = line.strip("\n")
        result.append(line)
    f.close()
    return result


import gc


def dump_garbage():
    """
    show us what's the garbage about
    """

    # force collection
    print "\nGARBAGE:"
    gc.collect()

    print "\nGARBAGE OBJECTS:"
    for x in gc.garbage:
        s = str(x)
        if len(s) > 80:
            s = s[:80]
        print type(x), "\n  ", s


def get_refcounts():
    d = {}
    sys.modules
    # collect all classes
    for m in sys.modules.values():
        for sym in dir(m):
            o = getattr(m, sym)
            if isinstance(o):
                d[o] = sys.getrefcount(o)

    # sort by refcount
    pairs = map(lambda x: (x[1], x[0]), d.items())
    pairs.sort()
    pairs.reverse()
    return pairs


def print_top_100():
    for n, c in get_refcounts()[:100]:
        print '%10d %s' % (n, c.__name__)


global_session_queue_mutex = threading.RLock()
if __name__ == '__main__':
    pass
