# Wireless Keystroke Injection (WKI) via Bluetooth Low Energy (BLE)

This software is a proof of concept (PoC) of a Wireless Keystroke Injection (WKI) vulnerability in Windows 10 (and 11) discovered by Layakk. This vulnerability allows a remote attacker to impersonate a Bluetooth Low Energy (BLE) keyboard and perform Wireless Key Injection (WKI) on its behalf. A legitimate BLE keyboard automatically closes its connection after a few minutes of inactivity. In that situation, an attacker can impersonate it and wirelessly send keys before the BLE "Encryption Start Procedure" is completed.
This is possible because of the combination of two facts:
* The BLE protocol allows a peripheral to send unencrypted LL messages before the completion of the Encryption Start Procedure.
* Windows systems do not correctly ensure that the encryption setup has been completed before accepting keystrokes.

## Prerequisites

The attack is implemented using [nRF52840 dongle](https://www.nordicsemi.com/Products/Development-hardware/nrf52840-dongle)  device.

You will also need to install following software to flash and run WKI:
* [nRFutil](https://infocenter.nordicsemi.com/index.jsp?topic=%2Fug_nrfutil%2FUG%2Fnrfutil%2Fnrfutil_intro.html) (for flashing only)
* Python3
* hcitool

## Flashing the Device

Before running the attack, the dongle should be flashed with our custom [firmware](firmware.zip). It can be flashed using nRFUtil as follows:

```
sudo nrfutil dfu usb-serial -pkg firmware.zip -p /dev/ttyACM0
```

## Running the attack

To perform the attack, the dongle should be configured and started using hci commands. To simplify this task we developed the script [kb_injection.py](kb_injection.py). This script gets the configuration, converts it into a sequence of hci commands and executes these commands (if you want).
The parameters used to configure the usb dongle are:

| Parameter | Format | Description |
| :-------: |:------ | :----- |
| -i | String hcidev | HCI Device to send the commands. |
| -m | String BDADDR | BDADDR of the keyboard to be impersonated. Format: XX:XX:XX:XX:XX:XX|
| -c | String PATH | Configuration file path. |
| -n | N/A | If present, do not execute hci commands. Just print them to stdout only. |
| -r | N/A | If present, run text_script in an endless loop (util conection is closed). |

This is an example of configuration file for one Microsoft Keyboard we tested:

```
{
  "REPORT_HANDLE":"0x0013"
  "REPORT_SIZE":11,
  "REPORT_OPTYPE":"0x1b",
  "TEXT_SCRIPT":"Write text here"
}
```

As can be seen in the example, some keyboard data is needed. We need to use a replica of target keyboard to know what is the handle used to send keystrokes (0x0013 in this case), the report size (11 bytes) and the operation used for sending reports (usually 0x1b, that is Notification).
The handle and report size can be extracted from Report Map (sent during GATT discovery) or found analizing the keyboard's replica behaviour.

The MAC (BDADDR) can be sniffed using a passive bluetooth sniffer.

The last item of the configuration, "TEXT_SCRIPT" is used to write the keystroke sequence to be injected.

Special characters can be used (see [HIDMapping.py](HIDMapping.py)). For example:
`{WIN_R}+r`
sends the key combination 'Windows key' and 'r key', as if they were pressed at same time, which opens the "Run" dialog in Windows OS.

This script also allows to insert a little delay between keystrokes using the command {SLEEP \<ms>}. For example:
`{SLEEP 500}`
will pause sending keys for 0.5 seconds.

Finally, you can use the special character '+' to send more than one key in the same report. For example:
`a+b+c`
sends "abc" as if those three keys were pressed simultaneously. They are all sent within the same report message.

You can see some examples in the "conf" folder.

## Related Links

[CVE-2022-30144](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2022-30144)

[Whitepaper](https://www.layakk.com/blog/wireless-keystroke-injection-vulnerability)
 
DEFCON Conference [slides](https://media.defcon.org/DEF%20CON%2030/DEF%20CON%2030%20presentations/Jose%20Pico%20%20%20Fernando%20Perera%20-%20Wireless%20Keystroke%20Injection%20%28WKI%29%20via%20Bluetooth%20Low%20Energy%20%28BLE%29.pdf)

## Authors

[Layakk Seguridad Informatica S.L.](https://www.layakk.com)

