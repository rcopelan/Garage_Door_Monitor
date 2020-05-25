""" Monitors a GPIO pin for change of state. """
# 20171022 rcopelan: changed AIO fred key from "garagedoor" to "home.garagedoor"
# 20171215 rcopelan: added "do car check" logic
# 201908xx rcopelan: added MQTT feed
# 20190918 rcopelan: changed to python3, removed mySQL (due to MQTT to Data Lake) & car detection
# 20191001 rcopelan: added timestamp to Robert's SMS message
# 20200522 rcopelan: updated config to come from a separate file, loop sending email with a
#                    refresh on config when door changes state
#

import configparser
#import datetime
#from email.mime.text import MIMEText
#from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart  import MIMENonMultipart
#import os
import smtplib
import syslog
import time

from Adafruit_IO import *
import paho.mqtt.client as mqtt
import RPi.GPIO as io

def on_connect(client1, userdata, flags, rc):
    """ prints the time that of connection to MQTT. """
    print("client:", client1)
    print("userdata:", userdata)
    print("flags:", flags)
    print("rc:", rc)
    print(time.strftime("%Y-%m-%d %H:%M:%S"), " Connected to broker\n\r")

def send_sms_email(filepath, new_door_state):
    """ Sends the email for door status change. """
    config = configparser.ConfigParser()
    config.read(filepath)
    smtp_server = config.get('smtp', 'smtp_server')
    smtp_port = config.get('smtp', 'smtp_port')
    smtp_user = config.get('smtp', 'smtp_user')
    smtp_password = config.get('smtp', 'smtp_password')

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)
    time.sleep(1)

    msg = ""
    for email_addr, when_sms in config.items('email'):
        send_message = True
        if (new_door_state == "Open"):
            if (when_sms == "closed"):
                send_message = False
        if send_message:
            mmsg2 = MIMENonMultipart('text', 'plain', charset='utf-8')
            mmsg2["Subject"] = "Door: " + new_door_state
            mmsg2["From"] = "rcopelan@gmail.com"
            mmsg2["To"] = email_addr
            mmsg2["Cc"] = ""
            msg = " "
            mmsg2.set_payload(msg)
            server.sendmail(mmsg2["From"], mmsg2["To"].split(",") +
                            mmsg2["Cc"].split(","), mmsg2.as_string())
    server.quit()

def main():
    """ Main program. """
    filepath = 'door_monitor.cfg'
    config = configparser.ConfigParser()
    config.read(filepath)

    broker_address = config.get('mqtt', 'broker_address')
    door_pin = config.getint('sensor', 'door_pin')
    ADAFRUIT_IO_KEY = config.get('aio', 'ADAFRUIT_IO_KEY')
    debug_flag = config.getboolean('flags', 'debug_flag')
    send_to_adafruit = config.getboolean('flags', 'send_to_Adafruit')

    client = mqtt.Client("G1") #create new instance
    client.on_connect = on_connect
    client.connect(broker_address) #connect to broker

    syslog.syslog(syslog.LOG_ERR, 'Starting ' + __file__)
    #
    # Setup GPIO
    #
    io.setmode(io.BCM)
    io.setwarnings(False)
    io.setup(door_pin, io.IN, pull_up_down=io.PUD_UP)

    current_door_state = "Closed"
    new_door_state = "Closed"
    #
    # Create an instance of the Adafruit_IO REST client.
    #
    aio = Client('wb4dhc', ADAFRUIT_IO_KEY)

    while True:
        if io.input(door_pin):
            new_door_state = "Open"
            if debug_flag:
                print("Door Open  ")
        else:
            new_door_state = "Closed"
            if debug_flag:
                print("Door Closed")

        if (new_door_state != current_door_state):
            if debug_flag:
                print("Door State changed from ", current_door_state, " to ", new_door_state)
            current_door_state = new_door_state
            if debug_flag:
                print("Door State changed to: %s" % current_door_state)
            aio_msg = new_door_state
            client.reconnect()
            client.publish("home/garage/door/status", current_door_state)
            client.publish("log/garage/door/status", current_door_state)
            client.publish("homie/garage/$nodes", "door", retain=True)
            client.publish("homie/garage/door/$properties", "status", retain=True)
            client.publish("homie/garage/door/status", current_door_state, retain=True)

            send_sms_email(filepath, new_door_state)

            if send_to_adafruit:
                aio.send('home.garagedoor', aio_msg)

        time.sleep(0.5)

if __name__ == '__main__':
    main()
