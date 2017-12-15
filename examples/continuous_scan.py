# ANT - Cadence, Speed Sensor AND Heart Rate Monitor - Example
#
# Copyright (c) 2017, H Ishizuka
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from __future__ import absolute_import, print_function

from ant.easy.node import Node
from ant.easy.channel import Channel
from ant.base.message import Message
from ant.base.commons import format_list

import logging
import struct
import threading
import sys

NETWORK_KEY= [0xb9, 0xa5, 0x21, 0xfb, 0xbd, 0x72, 0xc3, 0x45]

class Monitor():
    def __init__(self):
        self.heartrate = "n/a";
        self.cadence = "n/a";
        self.speed = "n/a";

    def on_data_heartrate(self, data):
        self.heartrate = str(data[7])
        self.display()

    def on_data_cadence_speed(self, data):
        self.cadence = str(data[3]*256 + data[2])
        self.speed = str(data[7]*256 + data[6])
        self.display()

    def on_data_speed(self, data):
        self.speed = str(data[7]*256 + data[6])
        self.display()
    
    def on_data_cadence(self, data):
        self.cadence = str(data[7]*256 + data[6])
        self.display()
    
    def on_data_scan(self, data):
        ant_id = data[10]*256 + data[9]
        ant_type = data[11]
        if ant_type == 120:
          self.on_data_heartrate(data)
        elif ant_type == 121:
          self.on_data_cadence_speed(data)
        elif ant_type == 122:
          self.on_data_cadence(data)
        elif ant_type == 123:
          self.on_data_speed(data)
        else:
          print(format_list(data))


    def display(self):
        string = "Hearthrate: " + self.heartrate + " Pedal revolutions: " + self.cadence + " Wheel revolutions: " + self.speed

        sys.stdout.write(string)
        sys.stdout.flush()
        sys.stdout.write("\b" * len(string))


def main():
    # logging.basicConfig()

    monitor = Monitor()

    node = Node()
    node.set_network_key(0x00, NETWORK_KEY)

    scan = node.new_channel(Channel.Type.BIDIRECTIONAL_RECEIVE)

    scan.on_broadcast_data = monitor.on_data_scan
    scan.on_burst_data = monitor.on_data_scan
    scan.set_rf_freq(57)
    scan.set_id(0, 0, 0)
    node.set_extended_message(1)

    try:
        node.continuous_scan()
        node.ant.set_wait_scan()
        node.start()
    finally:
        node.stop()
    
if __name__ == "__main__":
    main()

