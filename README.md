# HackBot

This bot was built in two CSR1000v virtual machines with three Host only Network adapters as shown below.

![image](https://user-images.githubusercontent.com/30132417/145153336-22ca423d-95ca-42fe-84a0-5973b1c0e804.png)

Ansible, Genie Robot, and Paramiko have been fully integrated and are elaborated on below.


---
Webex bot initial configuration

1. First you will need to go to https://developer.webex.com/ and create a chat bot. you will need to generate an eamil and token for the bot.
after you have done that you will need to open up the 381Bot.py file and add the token and the email into the bot_details area.

	- in the 381Bot.py file you will need to add in your router ips and passwords to connect.

2. Need to insall the ngrok application. After taht need you need to open up a terminal and run the command "ngrok http 5000" command. after this starts you will need to copy the forwarding address and add it the infomation to the "bot_url" section in 381Bot.py. 

3. Need to go to webex and open up and chat window with the bot you created. This will be the email you gave it. After you have opend up a chat window with you bot or invited it to your chatroom you can type /help to get a list of commands then you can use to interact with your network devices. You should now be able to interact with and secure your network with the network monitoring bot.

The command /help can be used for a quick overview of all of the skills of HackBot

![image](https://user-images.githubusercontent.com/30132417/145152603-5f03c9f9-e7ac-4b52-8201-94d0bb6c925b.png)


---

How to set up the paramiko module

1. Import paramiko and time, we will need these to use paramiko infrastructure and pause to give the router some time to respond.

	import paramiko
	
	import time

2. Set up the module to use SSH to connect to the routers, as well as an array of the 2 router devices we will be configuring.

    ssh_client= paramiko.SSHClient()  
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    router1 = {'hostname': '192.168.56.101', 'port': '22', 'username':'cisco', 'password':'cisco123!'}
    router2 = {'hostname': '192.168.56.102', 'port': '22', 'username':'cisco', 'password':'cisco123!'}
    routers = [router1, router2]

3. Create a loop that will run through the array and send the needed commands to get our output and close the SSH connection.


        for router in routers:
        ssh_client.connect(**router, look_for_keys=False, allow_agent=False)  
        print(f'Connecting to {router["hostname"]}')

        shell = ssh_client.invoke_shell()

        shell.send('en\n') 
        time.sleep(1)

        shell.send('show run \n')
        time.sleep(1)

        output = shell.recv(10000)
        output = output.decode('utf-8') 

        ssh_client.close()

4. Use python to find the command in the running-config. If it exists, it will return that passwords are encrypted along with the router IP. If not,
then the module will return that the encryption.

       if "service password-encryption" in output:
           testresponse += "Passwords are encrypted on" + (f' {router["hostname"]}.\n ') 
        else:
            testresponse += "No encryption found on" + (f' {router["hostname"]}!\n ')
    return testresponse

5. Add the module to the bot commands.

bot.add_command("Check encryption", "Check for Encryption on the routers", checkEncryption )

How to set up the ansible module

1. Install the ansible runner module.

	Dev# pip install ansible_runner
2. Create a name to your OSPF_setup.yaml

--- 
- name: CONFIGURE OSPF ADDRESSING 
  hosts: hosts
  gather_facts: false 
  connection: local 
 

3. Give it a task list with the following paramters.
  tasks: 
   - name: OSPF SETUP
     ios_config:
        parents: "router ospf 1"
        lines:
            - network 192.168.0.0 0.0.0.255 area 0

   - name: SET OSPF authentication  
     ios_config: 
       parents: "interface GigabitEthernet1" 
       lines: 
         - description OSPF interface
         - ip ospf authentication-key cisco

   - name: SHOW IPv4 INTERFACE SHOW RUN  
     ios_command: 
       commands: 
         - show run | section interface

     register: output 
 
   - name: SAVE OUTPUT ./ios_configurations/ 
     copy:  
       content: "{{ output.stdout[0] }}" 
       dest: "ios_configurations/Interface_configuration_{{ inventory_hostname }}.txt" 
   - name: SHOW RUN OSPF  
     ios_command: 
       commands: 
         - show run | section router ospf

     register: output 
 
   - name: SAVE OUTPUT ./ios_configurations/ 
     copy:  
       content: "{{ output.stdout[0] }}" 
       dest: "ios_configurations/OSPF_{{ inventory_hostname }}.txt" 


4. Create a new function in the 381.py file.

def OSPFsetup(incoming_msg):
import ansible_runner

5. Use the ansible-runner module to run an inline command in python.

out, err, rc = ansible_runner.run_command(
        executable_cmd = 'ansible-playbook',
        cmdline_args=['OSPF_Setup.yaml', '-i', 'hosts.txt'],
        input_fd=sys.stdin,
        output_fd=sys.stdout,
        error_fd=sys.stderr, )

6. Return whether or not the OSPF configuration was successful, otherwise return that it failed.

    if (int(format(rc)) == 0):
        return ("OSPF is configured and is using authenticaton")
    else:
        return ("Ansible has run into issues, please correct them")

7. Add the function to the bot commands.

bot.add_command("ospf", "Enables OSPF Authentication", OSPFsetup)

Example of Ansible bot running a script:

![image](https://user-images.githubusercontent.com/30132417/145153762-245db173-92dc-4faa-b212-7fda553f2202.png)

---

How to start setting up Genie Disaster Response

1. Create the script to monitor the vpn connection between static R1 interface G2 (172.168.0.1) and the dynamic R2 interface G2 (starting as 172.168.0.1)

	-This is done by doing some small modifications to the Monitor_Interfaces module installed with the other Genie Monitor tools.
	
	-Modifying the 'learn interfaces' function to output the ip address of the G2 interface allows the 381Bot.py to compare old and new messages works. 
	
	    def learn_interface(self):
		text=""
		for dev in self.device_list:
		    self.parser = ShowIpInterfaceBrief(dev)
		    out = self.parser.parse()
		    #print(out)
		    self.intf1 = []
		    text = out['interface']['GigabitEthernet2']['ip_address']
		    
2. Once the script is finished, it must be implimented into the 381Bot.py file.

	-Add a function called check_vpn to mimic the pre-existing check_int function. This allows the script to execute (after adding the command to the bottom of the file with the bot.addcommand() function.
	
	-Add a function called monitor_vpn that begins the monitoring, as well as a function to start a continuous job. 

3. This next part will be included in the next update

	-Add a function to the 381Bot.py to fix the vpn if the responses of the monitoring thread dont match up. This will make it easy to leave it running with no worries about if the dynamic address will change.

