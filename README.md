# Bluetooth temperature device scanner

A small library to scan for bluetooth devices and publishes their results to a mqtt broker.

*Requires* a custom `config.json` file which can be created based on `config.json.example` in this repository. More information below.

Used and tested with [Brifit Bluetooth thermometer and hygrometer, wireless](https://www.amazon.de/dp/B08DLHFKT3?ref_=cm_sw_r_cp_ud_dp_GBFCDBT8C64ZBJYJWDWW)
Probably the devices listed in https://github.com/iskalchev/ThermoBeacon-pyhap will work as well.

`tb_protocol.py` is taken from https://github.com/iskalchev/ThermoBeacon-pyhap.

## Install instructions

To run this following installations need to be made:

```
sudo apt-get install libglib2.0-dev
sudo pip3 install bluepy
sudo pip3 install HAP-python
sudo pip3 install paho-mqtt
```

## Configuration

The configuration defines how to connect to the broker and which devices are in use.
An example of a full configuration can be found in `config.json.example`. `config.json` is ignored via `.gitignore` so the own
configuration can be kept there without changes when updating the repository.

```
{
  "mqtt": {
    "user": "",
    "password": "",
    "port": 1883,
    "host": "my.broker.host",
    "keepalive": 60,
    "base_topic": "ble/temp"
  },
  "devices": {
    "73:06:00:00:09:45": {
      "name": "livingroom",
      "ignore": false
    },
    "8e:72:00:00:11:01": {
      "name": "bedroom",
      "ignore": true
    }
  }
}
```

### `mqtt`

<dl>
<dt>`user`</dt>
<dd>The username which is required to login to the broker – optional</dd>
<dt>`password`</dt>
<dd>The password which is required to login to the broker – optional</dd>
<dt>`port`</dt>
<dd>The port where the broker listens – mandatory</dd>
<dt>`host`</dt>
<dd>The hostname or ip where the broker listens – mandatory</dd>
<dt>`keepalive`</dt>
<dd>Keepalive setting for the mqtt connection – in seconds, mandatory. In most cases it is fine to leave this at 60 seconds.</dd>
<dt>`base_topic`</dt>
<dd>The topic name under which the device data will be published – mandatory. Each device gets a subpath under this topic.</dd>
</dl>

### `devices`

Objects of device mappings. The key of the object represents the mac address of the device. Mac addresses are printed
to stdout when `scan_publisher.py` is started.

<dl>
<dt>`name`</dt>
<dd>A friendly name of the device which will be used when publishing info to the broker – optional</dd>
<dt>`ignore`</dt>
<dd>When set to `false` no information of this device will be published. This might be useful when the application runs on several hosts which all have the same device in range. So only one application will publish the info.</dd>
</dl>

### Example

#### Device without configuration

For a base_topic `ble/temp` and a device with the mac address `aa:bb:cc:dd:ee:ff` the info for that device is published under
`ble/temp/aa:bb:cc:dd:ee:ff`.

#### Device with configuration

Assume the device has a configured name `livingroom`.

```
...
  "devices": {
    "aa:bb:cc:dd:ee:ff": {
      "name": "livingroom"
    },
...
```

This will publish under `ble/temp/livingroom`.

#### Ignored devices

When a device is ignored it won't publish its data to the broker. This might be set when another instance of this app runs on a different
host which has the same device in range and receives its information.

```
...
  "devices": {
    "aa:bb:cc:dd:ee:ff": {
      "name": "livingroom",
      "ignore": true
    },
...
```

Won't be published.

### Expected data

The data which will be published contains the following in JSON format:

<dl>
<dt>`mac`</dt>
<dd>The physical address of the device as string. Like in our examples above "aa:bb:cc:dd:ee:ff"</dd>
<dt>`temperature`</dt>
<dd>A floatingpoint number indicating the current measured temperature. Like 20.56</dd>
<dt>`humidity`</dt>
<dd>A floatingpoint number indicating the current measured humidity. Like 53.88</dd>
<dt>`button`</dt>
<dd>Indicator if the button of the device is currently pressed or not. Like "Off"</dd>
<dt>`battery`</dt>
<dd>The current charge state of the battery in percent. Like 87</dd>
<dt>`uptime`</dt>
<dd>The uptime of the device in seconds. Like 3272744</dd>
<dt>`name`</dt>
<dd>The name of the device as string. Either the looked up friendly name from the configuration as in our example "livingroom" or the mac address when no name is specified.</dd>
</dl>
