echo "NEOLS Signals Configuration Script"

echo "Setting Up the LoRa Modem"
meshtastic --set lora.region US
meshtastic --set lora.modem_preset SHORT_FAST
set /P varname="Enter the name of the signal: "
meshtastic --set-owner %varname%
set /P varid="Enter the ID of the signal: "
meshtastic --set-owner-short  %varid%

echo "Setting Up GPIO for Signal Indications"
meshtastic --set remote_hardware.enabled true

echo "Setting Up GPIO for Claims and Releases"
meshtastic --set detection_sensor.enabled true
meshtastic --set detection_sensor.minimum_broadcast_secs 5
meshtastic --set detection_sensor.name "Claim"
meshtastic --set detection_sensor.monitor_pin 6
meshtastic --set detection_sensor.detection_triggered_high true