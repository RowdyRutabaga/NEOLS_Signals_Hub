import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import serial.tools.list_ports   # Package Used to Enumerate Serial Ports
import threading
from meshtastic.util import (
    active_ports_on_supported_devices,
    detect_supported_devices,
    get_unique_vendor_ids,
)

# Local Scripts
from LoRa_Backend import LoRa_Hub_Thread

class Signal_Master_GUI(QWidget):
   def __init__(self, parent = None):
      super(Signal_Master_GUI, self).__init__(parent)
      
      layout = QHBoxLayout()
      self.cb = QComboBox()
      
      # simple arg check
      if len(sys.argv) != 1:
         print(f"usage: {sys.argv[0]}")
         print("Detect which device we might have.")
         sys.exit(3)

      vids = get_unique_vendor_ids()
      print(f"Searching for all devices with these vendor ids {vids}")

      sds = detect_supported_devices()
      if len(sds) > 0:
         print("Detected possible devices:")
      for d in sds:
         print(f" name:{d.name}{d.version} firmware:{d.for_firmware}")

      ports = active_ports_on_supported_devices(sds)
      print(f"ports:{ports}")
      for port in ports:
         self.cb.addItem(str(port).split(" ")[0])
      self.connect_button = QPushButton()
      self.connect_button.setText("Connect")
      self.connect_button.clicked.connect(self.connect_to_hub)		
      layout.addWidget(self.cb)
      layout.addWidget(self.connect_button)
      self.setLayout(layout)
      self.setWindowTitle("NEOLS SignalMaster")

   def connect_to_hub(self):
      self.com_port = self.cb.currentText()
      self.connect_button.setDisabled(True)

      # Create a new worker thread.
      self.createWorkerThread()

   def createWorkerThread(self):

      # Setup the worker object and the worker_thread.
      self.lora_hub = LoRa_Hub_Thread(self.com_port)
      self.lora_hub_thread = QThread()
      self.lora_hub.moveToThread(self.lora_hub_thread)
      self.lora_hub_thread.start()

      # Connect any worker signals
      self.lora_hub.received_packet_signal.connect(self.update_status)

   def forceWorkerReset(self):      
      if self.lora_hub_thread.isRunning():
         print('Terminating thread.')
         self.lora_hub_thread.terminate()

         print('Waiting for thread termination.')
         self.lora_hub_thread.wait()

         print('building new working object.')
         self.createWorkerThread()

   def forceWorkerQuit(self):
      if self.lora_hub_thread.isRunning():
         self.lora_hub_thread.terminate()
         self.lora_hub_thread.wait()
   
   @pyqtSlot(dict)
   def update_status(self, raw_packet):
      source_address = raw_packet['fromId']
      message = raw_packet['decoded']['payload']
		
def main():
   app = QApplication(sys.argv)
   ex = Signal_Master_GUI()
   ex.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()