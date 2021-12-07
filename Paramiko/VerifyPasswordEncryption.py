import paramiko
import time

ssh_client= paramiko.SSHClient()  
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

router1 = {'hostname': '192.168.56.101', 'port': '22', 'username':'cisco', 'password':'cisco123!'}
router2 = {'hostname': '192.168.56.102', 'port': '22', 'username':'cisco', 'password':'cisco123!'}
routers = [router1, router2]
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

    if "service password-encryption" in output:
        print ("Passwords are encrypted")
    else:
        print ("No encryption found!")