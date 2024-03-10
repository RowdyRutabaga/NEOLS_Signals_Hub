import meshtastic
import meshtastic.serial_interface
from pubsub import pub
from time import sleep
from datetime import datetime
import timeago
from PyQt5.QtCore import QObject, pyqtSignal,QThread
import os
#from meshtastic import remote_hardware
#from meshtastic.remote_hardware import onGPIOreceive
from meshtastic import admin_pb2
import meshtastic.test
import meshtastic.util
from meshtastic import channel_pb2, config_pb2, portnums_pb2, remote_hardware
from meshtastic.__init__ import BROADCAST_ADDR
from meshtastic.ble_interface import BLEInterface
from meshtastic.globals import Globals
import argparse
import logging
import os
import platform
import sys
import time

import pkg_resources
import pyqrcode
import yaml
from google.protobuf.json_format import MessageToDict
from pubsub import pub

class LoRa_Hub_Thread(QObject):
    received_packet_signal = pyqtSignal(dict)

    def __init__(self, com_port:str, parent = None):
        super(self.__class__, self).__init__(parent)

        # By default will try to find a meshtastic device,
        # otherwise provide a device path like /dev/ttyUSB0
        print(com_port)
        self.interface = meshtastic.serial_interface.SerialInterface(com_port)
        self.remote_hardware_client = RemoteHardwareClient(self.interface)
        # or something like this
        # interface = meshtastic.serial_interface.SerialInterface(devPath='/dev/cu.usbmodem53230050571')

        # or sendData to send binary data, see documentations for other options.
        Long_Name = self.interface.getLongName()
        Short_Name = self.interface.getShortName()
        print(Long_Name)
        print(Short_Name)
        self.interface.sendText("Hub Connected to PC!")
        self.localNode = meshtastic.node.Node(self, -1)  # We fixup nodenum later
        
        self.node_list = self.get_mesh_stats()
        self.node_dict_name_to_id = {}
        self.node_dict_id_to_name = {}
        for i in self.node_list:
            node_name = i['User']
            node_id = i['ID']
            self.node_dict_name_to_id[node_name] = node_id
            self.node_dict_id_to_name[node_id] = node_name
        print(self.node_dict_name_to_id)

        # self.build_mesh_dict()
        # if "Chessie_Loop_0" not in list(self.node_dict_name_to_id.keys()):
        #     self.build_mesh_dict()

        pub.subscribe(self.onReceive, "meshtastic.receive.data")
        for i in list(self.node_dict_name_to_id.keys()):
            self.off_indication(i)
        self.interface.sendText("Signals Ready!")
        print("Ready!")

    def onReceive(self, packet): # called when a packet arrives
        self.received_packet_signal.emit(packet)
        source_address = packet['fromId']
        message = packet['decoded']['payload']
        if b"Claim detected" in message:
            print(f"Claim Received from {self.node_dict_id_to_name[source_address]}")
            for i in self.node_list:
                if i['User'] == self.node_dict_id_to_name[source_address]:
                    pass
                else:
                    self.stop_indication(i['User'])
                node = self.interface.getNode(self.node_dict_name_to_id[i['User']],False)
                # Handle the int/float/bool arguments
                pref = ["detection_sensor.monitor_pin","7"]
                found = False
                field = self.splitCompoundName(pref[0].lower())[0]
                print(field)
                for config in [node.localConfig, node.moduleConfig]:
                    config_type = config.DESCRIPTOR.fields_by_name.get(field)
                    if config_type:
                        if len(config.ListFields()) == 0:
                            node.requestConfig(
                                config.DESCRIPTOR.fields_by_name.get(field)
                            )
                        found = self.setPref(config, pref[0], pref[1])
                        if found:
                            break
                if found:
                    print("Writing modified preferences to device")
                    while True:
                        try:
                            node.writeConfig(field)
                            self.interface.waitForAckNak()
                        except:
                            continue
                        break
                else:
                    print("Odd Error")
                pref = ["detection_sensor.name","Release"]
                found = False
                field = self.splitCompoundName(pref[0].lower())[0]
                print(field)
                for config in [node.localConfig, node.moduleConfig]:
                    config_type = config.DESCRIPTOR.fields_by_name.get(field)
                    if config_type:
                        if len(config.ListFields()) == 0:
                            node.requestConfig(
                                config.DESCRIPTOR.fields_by_name.get(field)
                            )
                        found = self.setPref(config, pref[0], pref[1])
                        if found:
                            break
                if found:
                    print("Writing modified preferences to device")
                    while True:
                        try:
                            node.writeConfig(field)
                            self.interface.waitForAckNak()
                        except:
                            continue
                        break
                else:
                    print("Odd Error")
            self.approach_indication(self.node_dict_id_to_name[source_address])
            self.interface.sendText("Claim Complete!")


        if b"Release detected" in message:
            print(f"Release Received from {self.node_dict_id_to_name[source_address]}")
            for i in self.node_list:
                self.off_indication(i['User'])
                node = self.interface.getNode(self.node_dict_name_to_id[i['User']],False)
                # Handle the int/float/bool arguments
                pref = ["detection_sensor.monitor_pin","6"]
                found = False
                field = self.splitCompoundName(pref[0].lower())[0]
                print(field)
                for config in [node.localConfig, node.moduleConfig]:
                    config_type = config.DESCRIPTOR.fields_by_name.get(field)
                    if config_type:
                        if len(config.ListFields()) == 0:
                            node.requestConfig(
                                config.DESCRIPTOR.fields_by_name.get(field)
                            )
                        found = self.setPref(config, pref[0], pref[1])
                        if found:
                            break
                if found:
                    print("Writing modified preferences to device")
                    while True:
                        try:
                            node.writeConfig(field)
                            self.interface.waitForAckNak()
                        except:
                            continue
                        break
                else:
                    print("Odd Error")
                pref = ["detection_sensor.name","Claim"]
                found = False
                field = self.splitCompoundName(pref[0].lower())[0]
                print(field)
                for config in [node.localConfig, node.moduleConfig]:
                    config_type = config.DESCRIPTOR.fields_by_name.get(field)
                    if config_type:
                        if len(config.ListFields()) == 0:
                            node.requestConfig(
                                config.DESCRIPTOR.fields_by_name.get(field)
                            )
                        found = self.setPref(config, pref[0], pref[1])
                        if found:
                            break
                if found:
                    print("Writing modified preferences to device")
                    node.writeConfig(field)
                    while True:
                        try:
                            node.writeConfig(field)
                            self.interface.waitForAckNak()
                        except:
                            continue
                        break
                else:
                    print("Odd Error")
            self.interface.sendText("Release Complete!")


    def get_mesh_stats(self):
        def formatFloat(value, precision=2, unit=""):
            """Format a float value with precision."""
            return f"{value:.{precision}f}{unit}" if value else None

        def getLH(ts):
            """Format last heard"""
            return (
                datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else None
            )

        def getTimeAgo(ts):
            """Format how long ago have we heard from this node (aka timeago)."""
            return (
                timeago.format(datetime.fromtimestamp(ts), datetime.now())
                if ts
                else None
            )
        rows = []
        for node in self.interface.nodes.values():
            user = node.get("user")
            row = {"N": 0}
            if user:
                row.update(
                    {
                        "User": user.get("longName", "N/A"),
                        "AKA": user.get("shortName", "N/A"),
                        "ID": user["id"],
                    }
                )
            metrics = node.get("deviceMetrics")
            if metrics:
                batteryLevel = metrics.get("batteryLevel")
                if batteryLevel is not None:
                    if batteryLevel == 0:
                        batteryString = "Powered"
                    else:
                        batteryString = str(batteryLevel) + "%"
                    row.update({"Battery": batteryString})
                row.update(
                    {
                        "Channel util.": formatFloat(
                            metrics.get("channelUtilization"), 2, "%"
                        ),
                        "Tx air util.": formatFloat(
                            metrics.get("airUtilTx"), 2, "%"
                        ),
                    }
                )
                row.update(
                    {
                        "SNR": formatFloat(node.get("snr"), 2, " dB"),
                        "Channel": node.get("channel"),
                        "LastHeard": getLH(node.get("lastHeard")),
                        "Since": getTimeAgo(node.get("lastHeard")),
                    }
                )

                rows.append(row)

        rows.sort(key=lambda r: r.get("LastHeard") or "0000", reverse=True)
        for i, row in enumerate(rows):
            row["N"] = i + 1
        return rows

    def clear_indication(self, node_name):
        """
        Turns off red and yellow Signal Lamps and turns on the green lamp on the specified node.
        """
        self.remote_hardware_client.writeGPIOs(self.node_dict_name_to_id[node_name],16,16)   # GPIO:4 mask:0x10 - Clear Indication
        self.remote_hardware_client.writeGPIOs(self.node_dict_name_to_id[node_name],8,0)    # GPIO:3 mask:0x8 - Approach Indication
        self.remote_hardware_client.writeGPIOs(self.node_dict_name_to_id[node_name],4,0)    # GPIO:2 mask:0x4 - Stop Indication
        print(f'{node_name} set to Clear')

    def approach_indication(self, node_name):
        """
        Turns off red and green Signal Lamps and turns on the yellow lamp on the specified node.
        """
        self.remote_hardware_client.writeGPIOs(self.node_dict_name_to_id[node_name],16,0)   # GPIO:4 mask:0x10 - Clear Indication
        self.remote_hardware_client.writeGPIOs(self.node_dict_name_to_id[node_name],8,8)    # GPIO:3 mask:0x8 - Approach Indication
        self.remote_hardware_client.writeGPIOs(self.node_dict_name_to_id[node_name],4,0)    # GPIO:2 mask:0x4 - Stop Indication
        print(f'{node_name} set to Approach')

    def stop_indication(self, node_name):
        """
        Turns off green and yellow Signal Lamps and turns on the red lamp on the specified node.
        """
        self.remote_hardware_client.writeGPIOs(self.node_dict_name_to_id[node_name],16,0)   # GPIO:4 mask:0x10 - Clear Indication
        self.remote_hardware_client.writeGPIOs(self.node_dict_name_to_id[node_name],8,0)    # GPIO:3 mask:0x8 - Approach Indication
        self.remote_hardware_client.writeGPIOs(self.node_dict_name_to_id[node_name],4,4)    # GPIO:2 mask:0x4 - Stop Indication
        print(f'{node_name} set to Stop')

    def off_indication(self, node_name):
        """
        Turns off all Signal Lamps on the specified node.
        """
        self.remote_hardware_client.writeGPIOs(self.node_dict_name_to_id[node_name],16,0)   # GPIO:4 mask:0x10 - Clear Indication
        self.remote_hardware_client.writeGPIOs(self.node_dict_name_to_id[node_name],8,0)    # GPIO:3 mask:0x8 - Approach Indication
        self.remote_hardware_client.writeGPIOs(self.node_dict_name_to_id[node_name],4,0)    # GPIO:2 mask:0x4 - Stop Indication
        print(f'{node_name} set to Off')

    def build_mesh_dict(self):
        node_list = self.get_mesh_stats()
        self.node_dict_name_to_id = {}
        self.node_dict_id_to_name = {}
        for i in node_list:
            if i['User'] == "NEOLS_Signals_Hub":
                pass
            else:
                node_name = i['User']
                node_id = i['ID']
                self.node_dict_name_to_id[node_name] = node_id
                self.node_dict_id_to_name[node_id] = node_name
        print(self.node_dict_name_to_id)

    def _sendAdmin(
        self,
        p: admin_pb2.AdminMessage,
        wantResponse=True,
        onResponse=None,
        adminIndex=0,
    ):
        """Send an admin message to the specified node (or the local node if destNodeNum is zero)"""

        if self.noProto:
            logging.warning(
                f"Not sending packet because protocol use is disabled by noProto"
            )
        else:
            if (
                adminIndex == 0
            ):  # unless a special channel index was used, we want to use the admin index
                adminIndex = self.iface.localNode._getAdminChannelIndex()
            logging.debug(f"adminIndex:{adminIndex}")

            return self.iface.sendData(
                p,
                self.nodeNum,
                portNum=portnums_pb2.PortNum.ADMIN_APP,
                wantAck=False,
                wantResponse=wantResponse,
                onResponse=onResponse,
                channelIndex=adminIndex,
            )

    def splitCompoundName(self,comp_name):
        """Split compound (dot separated) preference name into parts"""
        name = comp_name.split(".", 1)
        if len(name) != 2:
            name[0] = comp_name
            name.append(comp_name)
        return name
    
    def setPref(self,config, comp_name, valStr):
        """Set a channel or preferences value"""

        name = self.splitCompoundName(comp_name)

        snake_name = meshtastic.util.camel_to_snake(name[1])
        camel_name = meshtastic.util.snake_to_camel(name[1])
        logging.debug(f"snake_name:{snake_name}")
        logging.debug(f"camel_name:{camel_name}")

        objDesc = config.DESCRIPTOR
        config_type = objDesc.fields_by_name.get(name[0])
        pref = False
        if config_type and config_type.message_type is not None:
            pref = config_type.message_type.fields_by_name.get(snake_name)
        # Others like ChannelSettings are standalone
        elif config_type:
            pref = config_type

        if (not pref) or (not config_type):
            return False

        val = meshtastic.util.fromStr(valStr)
        logging.debug(f"valStr:{valStr} val:{val}")

        if snake_name == "psk" and len(valStr) < 8:
            print(f"Warning: wifi.psk must be 8 or more characters.")
            return False

        enumType = pref.enum_type
        # pylint: disable=C0123
        if enumType and type(val) == str:
            # We've failed so far to convert this string into an enum, try to find it by reflection
            e = enumType.values_by_name.get(val)
            if e:
                val = e.number
            else:
                if Globals.getInstance().get_camel_case():
                    print(
                        f"{name[0]}.{camel_name} does not have an enum called {val}, so you can not set it."
                    )
                else:
                    print(
                        f"{name[0]}.{snake_name} does not have an enum called {val}, so you can not set it."
                    )
                print(f"Choices in sorted order are:")
                names = []
                for f in enumType.values:
                    # Note: We must use the value of the enum (regardless if camel or snake case)
                    names.append(f"{f.name}")
                for temp_name in sorted(names):
                    print(f"    {temp_name}")
                return False

        # note: 'ignore_incoming' is a repeating field
        if snake_name != "ignore_incoming":
            try:
                if config_type.message_type is not None:
                    config_values = getattr(config, config_type.name)
                    setattr(config_values, pref.name, val)
                else:
                    setattr(config, snake_name, val)
            except TypeError:
                # The setter didn't like our arg type guess try again as a string
                config_values = getattr(config, config_type.name)
                setattr(config_values, pref.name, valStr)
        else:
            if val == 0:
                # clear values
                print("Clearing ignore_incoming list")
                del config_type.message_type.ignore_incoming[:]
            else:
                print(f"Adding '{val}' to the ignore_incoming list")
                config_type.message_type.ignore_incoming.extend([val])

        prefix = f"{name[0]}." if config_type.message_type is not None else ""
        if Globals.getInstance().get_camel_case():
            print(f"Set {prefix}{camel_name} to {valStr}")
        else:
            print(f"Set {prefix}{snake_name} to {valStr}")

        return True

    # Executed by default in a QThread
    def run():
        # Note: Without the sleep and while loop, nothing actually happens
        while True:
            QThread.yieldCurrentThread()
            sleep(1)








"""Remote hardware
"""
import logging

from pubsub import pub

from meshtastic import portnums_pb2, remote_hardware_pb2
from meshtastic.util import our_exit


def onGPIOreceive(packet, interface):
    """Callback for received GPIO responses"""
    logging.debug(f"packet:{packet} interface:{interface}")
    gpioValue = 0
    print(packet['decoded'])
    hw = packet["decoded"]["remotehw"]
    if 'GPIOS_CHANGED' in hw["type"]:
        print("Release!")
        gpioValue = 128
        mask = 128
    elif "gpioValue" in hw:
        gpioValue = hw["gpioValue"]
        mask = hw["gpioMask"]
    else:
        if not "gpioMask" in hw:
            # we did get a reply, but due to protobufs, 0 for numeric value is not sent
            # see https://developers.google.com/protocol-buffers/docs/proto3#default
            # so, we set it here
            gpioValue = 0
    value = int(gpioValue) & int(mask)
    print(
        f'Received RemoteHardware type={hw["type"]}, gpio_value={gpioValue} value={value}'
    )
    interface.gotResponse = True


class RemoteHardwareClient:
    """
    This is the client code to control/monitor simple hardware built into the
    meshtastic devices.  It is intended to be both a useful API/service and example
    code for how you can connect to your own custom meshtastic services
    """

    def __init__(self, iface):
        """
        Constructor

        iface is the already open MeshInterface instance
        """
        self.iface = iface
        ch = iface.localNode.getChannelByName("gpio")
        if not ch:
            our_exit(
                "Warning: No channel named 'gpio' was found.\n"
                "On the sending and receive nodes create a channel named 'gpio'.\n"
                "For example, run '--ch-add gpio' on one device, then '--seturl' on\n"
                "the other devices using the url from the device where the channel was added."
            )
        self.channelIndex = ch.index

        pub.subscribe(onGPIOreceive, "meshtastic.receive.remotehw")

    def _sendHardware(self, nodeid, r, wantResponse=False, onResponse=None):
        if not nodeid:
            our_exit(
                r"Warning: Must use a destination node ID for this operation (use --dest \!xxxxxxxxx)"
            )
        return self.iface.sendData(
            r,
            nodeid,
            portnums_pb2.REMOTE_HARDWARE_APP,
            wantAck=True,
            channelIndex=self.channelIndex,
            wantResponse=wantResponse,
            onResponse=onResponse,
        )

    def writeGPIOs(self, nodeid, mask, vals):
        """
        Write the specified vals bits to the device GPIOs.  Only bits in mask that
        are 1 will be changed
        """
        logging.debug(f"writeGPIOs nodeid:{nodeid} mask:{mask} vals:{vals}")
        r = remote_hardware_pb2.HardwareMessage()
        r.type = remote_hardware_pb2.HardwareMessage.Type.WRITE_GPIOS
        r.gpio_mask = mask
        r.gpio_value = vals
        return self._sendHardware(nodeid, r)

    def readGPIOs(self, nodeid, mask, onResponse=None):
        """Read the specified bits from GPIO inputs on the device"""
        logging.debug(f"readGPIOs nodeid:{nodeid} mask:{mask}")
        r = remote_hardware_pb2.HardwareMessage()
        r.type = remote_hardware_pb2.HardwareMessage.Type.READ_GPIOS
        r.gpio_mask = mask
        return self._sendHardware(nodeid, r, wantResponse=True, onResponse=onResponse)

    def watchGPIOs(self, nodeid, mask):
        """Watch the specified bits from GPIO inputs on the device for changes"""
        logging.debug(f"watchGPIOs nodeid:{nodeid} mask:{mask}")
        r = remote_hardware_pb2.HardwareMessage()
        r.type = remote_hardware_pb2.HardwareMessage.Type.WATCH_GPIOS
        r.gpio_mask = mask
        self.iface.mask = mask
        return self._sendHardware(nodeid, r)