#!/usr/bin/python


import logging as log
import sys
import time
from signal import *

import RPi.GPIO as GPIO

__author__ = 'tomek.ceszke'

IRSENSOR_RELAY_CH = 12
IRSENSOR_RECEIVER_CH = 22
SLEEP = 300


def send_email(subject, body):
    import smtplib
    import settings

    user = settings.user
    pwd = settings.pwd
    to = settings.recipient if type(settings.recipient) is list else [settings.recipient]
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (user, ", ".join(to), subject, body)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(user, to, message)
        server.close()
        log.debug('Sent the mail')
    except:
        log.error("Failed to send mail")


def setup():
    # GPIO
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(IRSENSOR_RELAY_CH, GPIO.OUT)  # , initial=GPIO.HIGH)
    GPIO.setup(IRSENSOR_RECEIVER_CH, GPIO.IN)  # , pull_up_down=GPIO.PUD_DOWN)
    # Logger
    log.basicConfig(filename='/var/log/irsensor.log', filemode='w', format='%(asctime)s %(levelname)s: %(message)s',
                    level=log.DEBUG)
    # Graceful exit
    for sig in (SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM):
        signal(sig, cleanup)


def toggle_irsensor(activated=True):
    if not activated:
        GPIO.output(IRSENSOR_RELAY_CH, GPIO.HIGH)
        log.info("IRSENSOR deactivated")
    else:
        GPIO.output(IRSENSOR_RELAY_CH, GPIO.LOW)
        log.info("IRSENSOR activated")
    time.sleep(1)


def monitor():
    log.info("Start monitoring...")
    while True:
        # GPIO.wait_for_edge(IRSENSOR_RECEIVER_CH, GPIO.RISING)
        if GPIO.input(IRSENSOR_RECEIVER_CH) == GPIO.LOW:
            time.sleep(0.1)
            if GPIO.input(IRSENSOR_RECEIVER_CH) == GPIO.LOW:
                log.warning("IR Alert!")
                send_email("IR Sensor", "Alarm!")
                toggle_irsensor(False)
                log.debug("Sleeping " + str(SLEEP) + " sec...")
                time.sleep(SLEEP)
                toggle_irsensor(True)
            else:
                log.warning("Fake alert")
        time.sleep(0.1)


def cleanup(*args):
    GPIO.output(IRSENSOR_RELAY_CH, GPIO.HIGH)
    GPIO.cleanup()
    log.debug("Cleaning up!")
    sys.exit(0)


def main():
    setup()
    toggle_irsensor()
    try:
        monitor()
    finally:
        cleanup()


if __name__ == '__main__':
    main()
