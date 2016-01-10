#!/usr/bin/env python
import zmq, json, sys, os
from datetime import datetime, timedelta

context = zmq.Context()
socket = context.socket(zmq.SUB)
topics = ['sunset', 'sunrise']
for topic in topics:
    socket.setsockopt_string(zmq.SUBSCRIBE, topic)
socket.bind("tcp://*:2342")
while True:
    topic, result = socket.recv_multipart()
    print(result)
