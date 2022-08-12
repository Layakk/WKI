
# HCI OPCODES
HCI_SET_RANDOM_ADDRESS              = "0x08 0x0005"
HCI_SET_ADV_PARAM                   = "0x08 0x0006"
HCI_SET_ADV_DATA                    = "0x08 0x0008"
HCI_SET_SCAN_RSP_DATA               = "0x08 0x0009"
HCI_SET_ADV_ENABLE                  = "0x08 0x000a"

HCI_VS_OPCODE_SETUP_ALL             = "0x3f 0x03f0"
HCI_VS_OPCODE_ACTIONS_CLEAN         = "0x3f 0x03e1"
HCI_VS_OPCODE_ACTIONS_ADD           = "0x3f 0x03e2"
HCI_VS_OPCODE_ACTIONS_RUN_FOREVER   = "0x3f 0x03e3"

ADDR_TYPE_PUBLIC                    = "0x00"
ADDR_TYPE_RANDOM                    = "0x01"


# CMD CONSTANTS
CMD_BASE = "hcitool -i {hci_dev} cmd {hci_op} {hci_args}"

class COMMAND_BUILDER:

    def __init__(self, hci_dev):
        self.device = hci_dev

    def cmd_dev_up(self):
        return "hciconfig {hci_dev} up".format(hci_dev=self.device)
    
    def cmd_dev_down(self):
        return "hciconfig {hci_dev} down".format(hci_dev=self.device)

    def cmd_set_random_addr(self, mac_address): #D8:F1:B3:82:92:D4
        splited_addr = mac_address.split(":")

        bdaddr = ""
        if (len(splited_addr) == 6):
            bdaddr = "0x" + splited_addr[5] + " 0x" + splited_addr[4] + " 0x" + splited_addr[3] + " 0x" + splited_addr[2] + " 0x" + splited_addr[1] + " 0x" + splited_addr[0]
        
        return CMD_BASE.format(hci_dev=self.device,  hci_op=HCI_SET_RANDOM_ADDRESS, hci_args=bdaddr)
    
    def cmd_set_adv_param(self, interval_min="0xA0 0x00", interval_max="0xA0 0x00", adv_type="0x00",
                self_addr_type=ADDR_TYPE_RANDOM, other_addr_type=ADDR_TYPE_PUBLIC,
                other_addr = "0x00 0x00 0x00 0x00 0x00 0x00",
                adv_channels = "0x05", adv_filter="0x00"):
        # ADV interval Min (2bytes) 160ms (0xA0 0x00)
        # ADV interval Max (2bytes) 160ms (0xA0 0x00)
        # ADV_TYPE (1byte) 
        # Own ADDR Type (1byte) 
        # Directed Address Type (1byte) 
        # Directed BDADDR (6bytes)
        # CHANEL MASK (1byte, 3 bits really)
        # ADV Filter Policy (1byte)
        # default: "0xA0 0x00 0xA0 0x00 0x00 0x01 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x05 0x00"

        return CMD_BASE.format(hci_dev=self.device,  hci_op=HCI_SET_ADV_PARAM,
            hci_args="{int_min} {int_max} {adv_type} {s_addr_type} {o_addr_type} {o_addr} {adv_channels} {adv_filter}".
                format(int_min=interval_min, int_max=interval_max, adv_type=adv_type, s_addr_type=self_addr_type,
                        o_addr_type=other_addr_type, o_addr=other_addr, adv_channels=adv_channels, adv_filter=adv_filter))

    def cmd_set_adv_data(self, adv_data):
        return CMD_BASE.format(hci_dev=self.device,  hci_op=HCI_SET_ADV_DATA, hci_args=adv_data)

    def cmd_set_scan_rsp_data(self, scan_rsp_data):
        return CMD_BASE.format(hci_dev=self.device,  hci_op=HCI_SET_SCAN_RSP_DATA, hci_args=scan_rsp_data)
    
    def cmd_start_advertising(self, start=True):
        if(start):
            start_adv = '0x01'
        else:
            start_adv = '0x00'

        return CMD_BASE.format(hci_dev=self.device,  hci_op=HCI_SET_ADV_ENABLE, hci_args=start_adv)

    def cmd_setup_all(self, report_handle, report_size, report_optype):
        return CMD_BASE.format(hci_dev=self.device, hci_op=HCI_VS_OPCODE_SETUP_ALL, hci_args=' '.join(
            ['0x%02x'%int(report_handle[-2:],16),
            '0x%02x'%int(report_handle[2:-2],16),
            '0x%02x'%report_size,
            '0x%02x'%int(report_optype,16)
            ]))
    
    def cmd_actions_clean(self):
        return CMD_BASE.format(hci_dev=self.device, hci_op=HCI_VS_OPCODE_ACTIONS_CLEAN, hci_args="")

    def cmd_actions_add(self, report):
        return CMD_BASE.format(hci_dev=self.device, hci_op=HCI_VS_OPCODE_ACTIONS_ADD, hci_args=' '.join(map(lambda y: '0x%02x'%(y%256), report)))

    def cmd_actions_run_forever(self):
        return CMD_BASE.format(hci_dev=self.device, hci_op=HCI_VS_OPCODE_ACTIONS_RUN_FOREVER, hci_args="")




