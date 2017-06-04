#!/usr/bin/env python
import shlex
import argparse
import subprocess
import sys
import os 

FIRM_PATH = "/tools/firmadyne" 
# EDIT THIS TO YOUR FIRMADYNE ROOT PATH 

parser = argparse.ArgumentParser(description="automates firmadyne emulation")
parser.add_argument('-f', '--file', help ="path to firmware file", required = True, default = None)
parser.add_argument('-b', '--brand', help ="brand of firmware", required = False, default = "Brand")
parser.add_argument('-s', '--sql', help ="sql server ip", required = False, default = "127.0.0.1")
parser.add_argument('-o', '--output', help ="output directory", required = False, default = FIRM_PATH + "/images")
args = parser.parse_args()

# Start Postgresql 
subprocess.call(["/etc/init.d/postgresql", "start"])
# Unmount in case 
subprocess.call(["umount", "-l", "/dev/mapper/loop0p1"])
# Stores the tarball in images
command = FIRM_PATH+"/sources/extractor/extractor.py -b " + args.brand + " -sql " + args.sql + " -np -nk " + "\"" + args.file + "\" " + args.output
print "Command: " + command
output = subprocess.check_output(shlex.split(command), shell=False)
#output = subprocess.check_output([FIRM_PATH+"/sources/extractor/extractor.py", "-b", args.brand, "-sql", args.sql, "-np", "-nk", "\"" + args.file + "\"", args.output], shell=False) 
print "Output: " + output
# Retrieve ID 
output = output.split("\n")
id = 1 
for i in output:
   if "Database" in i:
      id = i[-1:] # rely on id being at end 
      #print "ID is", id 

# Identify Architecture
command = FIRM_PATH + "/scripts/getArch.sh " + args.output + "/" + str(id) + ".tar.gz"
print "Command: " + command
output = subprocess.check_output(command.split(), shell=False)
print "Output: " + output 
architecture = output.split()[-1]
print "Architecture: " + architecture

# Populate DB 
command = FIRM_PATH + "/scripts/tar2db.py -i " + str(id) + " -f " + args.output + "/" + str(id) + ".tar.gz"
print "Command: " + command
try:
	output = subprocess.check_output(command.split(), shell=False)
except Exception, e:
	output = str(e.output)
print "Output: " + output 

# QEMU Disk Image 
command = "sudo " + FIRM_PATH + "/scripts/makeImage.sh " + str(id) + " " + architecture
print "Command: " + command
# Try Except block bc of ioctl remove bug 
try:
	output = subprocess.check_output(command.split(), shell=False)
except Exception, e:
        output = str(e.output)
        

print "Output: " + output 

# Infer Network Config 
command = FIRM_PATH + "/scripts/inferNetwork.sh " + str(id) + " " + architecture
print "Command: " + command
print "[*] After ~60 Seconds access" 
# Next part seems a little glitchy with the timing... 
output = subprocess.check_output(command.split(), shell=False)
#print "[*] About to emulate firmware"
print "Output: " + output 

# Emulate Firmware 
command = FIRM_PATH + "/scratch/" + str(id) + "/run.sh"
print "Command: " + command
output = subprocess.call(command.split(), shell=False)
#print "Output: " + output 