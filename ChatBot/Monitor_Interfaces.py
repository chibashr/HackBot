import time

# Genie import
from genie.conf import Genie

# import the genie libs
from genie.libs import ops # noqa

# Parser import
from genie.libs.parser.iosxe.show_interface import ShowIpInterfaceBrief

# Import Genie Conf
from genie.libs.conf.interface import Interface

class MonitorInterfaces():

    def setup(self, testbed):
        genie_testbed = Genie.init(testbed)
        self.device_list = []
        str = ""
        for device in genie_testbed.devices.values():
            try:
                device.connect()
            except Exception as e:
                print("Failed to establish connection to '{}'".format(
                    device.name))
                str += "\nFailed to establish connection to "+ device.name

            self.device_list.append(device)

        return str

    def learn_interface(self):
        text=""
        for dev in self.device_list:
            self.parser = ShowIpInterfaceBrief(dev)
            out = self.parser.parse()
            print(out)
            self.intf1 = []
            # let's find  the interface
            for interface, value in out['interface'].items():
                #print(interface)
                if 'down' in value['status']:
                    text+="\n"+interface +" on " + dev.name + " is down"
                    # Create a Genie conf object out of it
                    # This way, it will be OS/Cli/Yang Agnostic    
                    self.intf1.append(Interface(name=interface, device=dev))

        return text
    

if __name__ == "__main__":
    # Test Functions
    mon = MonitorInterfaces()
    mon.setup('testbed/routers.yml')
    intfl = mon.learn_interface()
    print(intfl)
