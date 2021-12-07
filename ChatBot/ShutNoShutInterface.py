import time

# Genie import
from genie.conf import Genie

# import the genie libs
from genie.libs import ops # noqa

# Parser import
from genie.libs.parser.iosxe.show_interface import ShowIpInterfaceBrief

# Import Genie Conf
from genie.libs.conf.interface import Interface

class ShutNoShutInterface():

    def learn_interface(self, uut, ifname):
        self.parser = ShowIpInterfaceBrief(uut)
        out = self.parser.parse()
        #print(out)

        # let's find  the interface
        for interface, value in out['interface'].items():
            print(interface)
            if interface == 'GigabitEthernet2':
                # found the interface
                interface = interface
                break
        else:
            # Could not find an interface
            self.skipped("Could not find an interface "
                         "for device '{u}'".format(u=uut.name),
                         goto=['next_tc'])

        # Create a Genie conf object out of it
        # This way, it will be OS/Cli/Yang Agnostic
        self.intf1 = Interface(name=interface, device=uut)
        print (self.intf1)

    def shut(self):
        # Call Genie Conf
        self.intf1.shutdown = True
        self.intf1.build_config()

    def noshut(self):
        # Call Genie Conf
        #self.intf1.build_unconfig()
        self.intf1.shutdown = False
        self.intf1.build_config()

if __name__ == "__main__":
    genie_testbed = Genie.init("testbed/routers.yml")
    device_list = []
    for device in genie_testbed.devices.values():
        #print("Connect to device '{d}'".format(d=device.name))
        try:
            device.connect()
        except Exception as e:
            print("Failed to establish connection to '{}'".format(
                device.name))

        device_list.append(device)
    trigger = ShutNoShutInterface()
    trigger.learn_interface(device_list[1], 'GigabitEthernet2')
    while(True):
        trigger.shut()
        time.sleep(2)
        trigger.noshut()
        time.sleep(30)
