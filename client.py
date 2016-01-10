import json
import zmq
import os
import logging
import sys
import signal
from datetime import date, datetime
from time import sleep
from astral import Astral
from apscheduler.schedulers.blocking import BlockingScheduler

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
socket_address = os.getenv('PROXY_SOCKET').strip()
os.environ['TZ'] = 'Europe/Stockholm'


def build_sun():
    a = Astral()
    a.solar_depression = 'astronomical'
    city = a['Stockholm']
    return city.sun(date=date.today(), local=True)


def send(socket, topic, message):
    socket.send_multipart(
            [topic, bytes(
                    json.dumps(
                            {'message': message, 'datetime': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")}),
                    'utf8')])


def add_todays_jobs(scheduler, socket):
    sun = build_sun()
    scheduler.add_job(send, 'date', run_date=sun['sunset'], args=(socket, b'sunset', "Sunset is here!"))
    scheduler.add_job(send, 'date', run_date=sun['sunrise'], args=(socket, b'sunrise', "Sunrise is here!"))


def signal_handler(signal, frame):
    print('You pressed Ctrl+C! Shutting down')
    socket.close(linger=1)
    sys.exit(0)


if __name__ == "__main__":
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    logging.info('Connected to address %s', socket_address)
    socket.connect(socket_address)
    scheduler = BlockingScheduler()
    add_todays_jobs(scheduler, socket)
    scheduler.add_job(add_todays_jobs, 'cron', day='*', hour='00', minute='5', args=(scheduler, socket))

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    scheduler.start()
    # try:
    # except (KeyboardInterrupt, SystemExit):
    #    print('Exiting!')
    #    socket.close(linger=1)
    #    context.destroy(linger=1)
