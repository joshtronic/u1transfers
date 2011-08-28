#!/usr/bin/env python

import threading
import time
import gobject
import gtk
import subprocess
import re
import md5

gobject.threads_init()

class MyThread(threading.Thread):
	def __init__(self, vbox):
		super(MyThread, self).__init__()
		self.vbox = vbox
		self.quit = False
		self.files = {}

	def update_label(self, counter):
		transfers = subprocess.check_output(["u1sdtool", "--current-transfers"])
		transfers = transfers.split("\n");

		for line in transfers:
			if re.match("Current uploads:", line) != None:
				transfer_type = 'Uploading'
			elif re.match("Current downloads:", line) != None:
				transfer_type = 'Downloading'
			else:
				if re.match("  path: ", line) != None:
					transfer_file = line.replace("  path: ", "")
				elif re.match("    deflated size: ", line) != None:
					total = line.replace("    deflated size: ", "")
				elif re.match("    bytes written: ", line) != None:
					transferred = line.replace("    bytes written: ", "")
					
					complete = int((float(transferred) / float(total)) * 100)

					m = md5.new()
					m.update(transfer_file)
					file_hash = m.digest()

					if file_hash not in self.files:
						label = gtk.Label(transfer_file)
						label.set_justify(gtk.JUSTIFY_LEFT)
						self.vbox.pack_end(label, True, True, 2)
						label.show()

						self.files[file_hash] = label
					
					if complete < 100:
						self.files[file_hash].set_text("[" + str(complete)  + "%] " + transfer_type + " " + transfer_file)
					else:
						self.files[file_hash].destroy()

		return False

	def run(self):
		counter = 0
		while not self.quit:
			counter += 1
			gobject.idle_add(self.update_label, counter)
			time.sleep(5)

w = gtk.Window()
w.set_title("Ubuntu One Active Transfers")
w.set_border_width(0)
w.set_size_request(800, 300)

v = gtk.VBox(False, 0)
w.add(v)
v.show()
        
w.show_all()
w.connect("destroy", lambda _: gtk.main_quit())
t = MyThread(v)
t.start()

gtk.main()
t.quit = True
