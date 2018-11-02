#!/usr/bin/python3
#(c) 2017 Todd Riemenschneider
#
#Enable Multiprocessing
from multiprocessing import Pool
#getpass will not display password
from getpass import getpass
#ConnectionHandler is the function used by netmiko to connect to devices
from netmiko import ConnectHandler
#Time tracker
from time import time

#create variables for username and password
#create variables for configs and hosts
uname = input("Username: ")
passwd = getpass("Password: ")

#This will allow you to just press enter
#This sets default values Not recommanded in any place but a lab
if len(uname) < 1 : uname = "admin"
if len(passwd) < 1 : passwd = "automate"

# To manually add hosts to scripts just follow the format below
#hosts = ["1.1.1.1", "2.2.2.2", "3.3.3.3", "4.4.4.4"]

# Pull target hosts from host_file
with open('host_file.txt') as f:
    hosts = f.read().splitlines()

cmds = ['show running-config', 'show version', 'show inventory', 'show interface description',
        'show ip arp', 'show ip route summary', 'show vlan brief', 'show vtp status',
        'show cdp neighbor', 'show lldp neighbor', 'show ip bgp summ', 'show ip ospf nei',
        'show ip eigrp nei', 'show interface status', 'show trunk', 'show int trunk', 'show etherchannel summ',
        'show mac address-table', 'show ip route 0.0.0.0', 'show spanning-tree brief']


starting_time = time()

#Each member of the pool of 5 will be run through this function
def run_script(host_ip):
    ios_rtr = {
        "device_type": "cisco_ios",
        "ip": host_ip,
        "username": uname,
        "password": passwd,
        }
    nl = "\n"
    try: 
        #connect to the device via ssh
        net_connect = ConnectHandler(**ios_rtr)
        host_name = net_connect.find_prompt()
        print("Connected to host:", host_ip)
        host_id = "Connected to host: " + host_ip
        print('\n---- Elapsed time=', time()-starting_time)
        for cmd in cmds:
            cmd_output = net_connect.send_command(cmd, use_textfsm=False)
            # Uncomment below to see all commands being run
            #print(cmd_output)
            with open(host_ip + "_cmds_file.txt", 'a') as file:
                file.write(host_id)
                file.write(nl)
                file.write(host_name)
                file.write(nl)
                file.write(cmd)
                file.write(nl)
                file.write(cmd_output)
                file.write(nl)
                file.write("**************************************")
                file.write(nl)

    except Exception as unknown_error:
        # Error handling - Print output to screen
        print("************************************")
        print("Unable to log into this device:", host_ip)
        print(unknown_error)
        print("************************************")
        # Error handling - record to file
        with open("Connection_Errors", "a") as err_log:
            err_log.write("Error connecting to the following devices")
            err_log.write(nl)
            err_log.write(str(unknown_error))
            err_log.write(nl)
            err_log.write(host_ip)
            err_log.write(nl)


if __name__ == "__main__":
    # Pool(5) means 5 process will be run at a time, more hosts will go in the next group
    with Pool(5) as p:
        print(p.map(run_script, hosts))