from MQTTLib import AWSIoTMQTTClient
from network import WLAN
import time
import config
import json
import machine
import pycom

# Connect to wifi
wlan = WLAN(mode=WLAN.STA)
wlan.connect(config.WIFI_SSID, auth=(None, config.WIFI_PASS), timeout=5000)
while not wlan.isconnected():
    time.sleep(0.6)
print('WLAN connection succeeded!')
print('\nnetwork config:', wlan.ifconfig())

rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")
time.sleep(0.75)
print('\nRTC Set from NTP to UTC:', rtc.now())
time.timezone(-14200)
print('Adjusted from UTC to EST timezone', time.localtime(), '\n')
print("Local time: ", time.localtime())
a = rtc.synced()
print('RTC is synced to "pool.ntp.org": ', a)

# user specified callback function
def customCallback(client, userdata, message):
	print("Received a new message: ")
	print(message.payload)
	print("from topic: ")
	print(message.topic)
	print("--------------\n\n")

# configure the MQTT client
pycomAwsMQTTClient = AWSIoTMQTTClient(config.CLIENT_ID)
pycomAwsMQTTClient.configureEndpoint(config.AWS_HOST, config.AWS_PORT)
pycomAwsMQTTClient.configureCredentials(config.AWS_ROOT_CA, config.AWS_PRIVATE_KEY, config.AWS_CLIENT_CERT)

pycomAwsMQTTClient.configureOfflinePublishQueueing(config.OFFLINE_QUEUE_SIZE)
pycomAwsMQTTClient.configureDrainingFrequency(config.DRAINING_FREQ)
pycomAwsMQTTClient.configureConnectDisconnectTimeout(config.CONN_DISCONN_TIMEOUT)
pycomAwsMQTTClient.configureMQTTOperationTimeout(config.MQTT_OPER_TIMEOUT)
#pycomAwsMQTTClient.configureLastWill(config.LAST_WILL_TOPIC, config.LAST_WILL_MSG, 1)

#Connect to MQTT Host
if pycomAwsMQTTClient.connect():
    print('AWS connection succeeded')

# Subscribe to topic
pycomAwsMQTTClient.subscribe(config.TOPIC, 1, customCallback)
time.sleep(2)

# Send message to host
loopCount = 0
value = 8.5
while loopCount < 15:
	year, month, day, hour, mins, secs, weekday, yearday = time.localtime()
	now="{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(year, month, day, hour, mins, secs)
	payload=json.dumps({"device_id": "001","temperature": 60,"humidity": 50,"timestamp": now});
	pycomAwsMQTTClient.publish(config.TOPIC, payload, 1)
	loopCount += 1
	time.sleep(5.0)
