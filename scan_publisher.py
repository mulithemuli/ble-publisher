#!/usr/bin/env python3

'''
Scanner tool for Brifit Bluetooth LE thermometer/hygrometer devices.
Shows the characteristics of the found devices
'''

import sys
from bluepy.btle import Scanner, DefaultDelegate

import tb_protocol

import paho.mqtt.client as mqtt

import json

class ScanDelegate(DefaultDelegate):

    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            pass
        if True or isNewData:
            #logger.debug('discobvery:' + dev.addr)

            complete_name=dev.getValueText(0x09)
            manufact_data=dev.getValueText(0xff)
            if complete_name is None or manufact_data is None:
                return
            bvalue=bytes.fromhex(manufact_data)
            if len(bvalue)!=20 or complete_name!='ThermoBeacon':
                return

            data = tb_protocol.TBAdvData(bvalue[0]+(bvalue[1]<<8), bvalue[2:])
            #print(manufact_data)
#            json_data = '{{"mac": "{0}", "temperature": {1:5.2f}, "humidity": {2:3.2f}, "button": "{4}", "battery": {5:02.0f}, "uptime": {3:.0f}}}'.\
#                  format(dev.addr, data.tmp, data.hum, data.upt, 'On ' if data.btn else 'Off', data.btr)
#            print(json_data)

            if dev.addr in config['devices'] and 'name' in config['devices'][dev.addr]:
              print('device lookup for ' + dev.addr + ' resulted in name: ' + config['devices'][dev.addr]['name'])
              dev_name = config['devices'][dev.addr]['name']
            else:
              print('using default device address instead of name for: ' + dev.addr)
              dev_name = dev.addr

            json_data = '{{"mac": "{0}", "temperature": {1:5.2f}, "humidity": {2:3.2f}, "button": "{4}", "battery": {5:02.0f}, "uptime": {3:.0f}, "name": "{6}"}}'.\
                  format(dev.addr, data.tmp, data.hum, data.upt, 'On ' if data.btn else 'Off', data.btr, dev_name)

            print('collected data: ' + json_data)

            if config['devices'].get(dev.addr) is None or config['devices'][dev.addr].get('ignore') is None or not config['devices'][dev.addr].get('ignore') is True:
              topic = config['mqtt']['base_topic'] + '/' + dev_name
              print('publishing to ' + topic)
              client.publish(topic, json_data)
            else:
              print('not publishing device ' + dev_name + ' since it is ignored')

def on_mqtt_connect(client, userdata, flags, rc):
  print('connected with result code ' + str(rc))

f = open('config.json')
config = json.load(f)
f.close()

if not 'devices' in config:
  print('no devices defined - using default empty')
  config['devices'] = json.loads('{}')

scanDelegate = ScanDelegate()
scanner = Scanner().withDelegate(scanDelegate)

client = mqtt.Client()
if 'user' in config['mqtt'] or 'password' in config['mqtt']:
  print('using user and password')
  if 'user' in config['mqtt']:
    user = config['mqtt']['user']
  else:
    user = ''
  if 'password' in config['mqtt']:
    password = config['mqtt']['password']
  else:
    password = ''
  client.username_pw_set(user, password)

client.on_connect = on_mqtt_connect
client.connect(config['mqtt']['host'], config['mqtt']['port'], config['mqtt']['keepalive'])

try:
  client.loop_start()
except KeyboardInterrupt:
  print('\nInterrupted')
  sys.exit(0)

while True:
    try:
        scanner.clear()
        scanner.start()
        scanner.process(20)
        scanner.stop()
    except Exception as exc:
        print(str(exc))
        pass
    except KeyboardInterrupt:
        print('\nInterrupted!')
        sys.exit(0)


