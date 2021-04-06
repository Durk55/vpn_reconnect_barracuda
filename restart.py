import requests
from datetime import datetime
import json 
import time 
import logging 
import urllib3 
import argparse
from requests.auth import HTTPBasicAuth 
urllib3.disable_warnings() 
logging.basicConfig(filename='vpnconnection.log', format='%(asctime)s,%(levelname)s,%(message)s', datefmt='%Y-%m-%d %I:%M:%S', level=logging.INFO) 

parser = argparse.ArgumentParser()
parser.add_argument('-fw', '--list', dest='fw',  nargs='+', required=False)
args = parser.parse_args()

class connectionRestoring:
    """
    This Class was made to restore VPN Connection with the Barracuda REST API
    Reads from a file named "fwlist.txt" the ip address, fw name and token. Saves them in 3 lists.
    Afterwards it gets a list of all VPN Tunnes on the firewalls and checks the status of the tunnel.
    Is the Status "down" or "down (disabled)", the script sends a post request to reinitiate the tunnel again.
    """
    def __init__(self):
        self.ip_addrs = [] 
        self.api_tokens = [] 
        self.fw_names = []
        self.tunnel_list = []
        self.single_list = []
    
    def clearList(self):
        self.ip_addrs = []
        self.api_tokens = []
        self.fw_names = []

    def getIpAndToken(self):
        """
        This Function get ip addresses and token from a file calles "fwlist" and puts each in a list.
        """
        try:
            with open('fwlist.txt', 'r') as f:
                cnt = 1
                missing = []
                for lines in f.readlines():
                    ip_addr, fw_name, api_token = lines.split(',')
                    if api_token.isspace() or fw_name.isspace() or ip_addr.isspace():
                        missing.append(cnt)
                        cnt += 1
                        continue
                    self.ip_addrs.append(ip_addr)
                    self.api_tokens.append(api_token.rstrip('\n'))
                    self.fw_names.append(fw_name)
                    cnt += 1
                print("Tokens missing in this rows:")
                print(missing)
        except OSError:
            print("Could not open file fwlist.txt. Maybe the file don't exist")

    def getVpnData(self):
        """ 
        Gets a list of IP Address, Token, FW Name, IP Tunnel Internal Name and Status
        Internal Name and Status are received through GET Command
        """
        for index in range(len(self.ip_addrs)):
            try:
                params_tunnels = { "name": "", "type": "", "transport": "", "encryption": "", "hashing": "", "local": "", "peer": "", "group": "", "envelope": True } 
                header = { "X-API-Token": self.api_tokens[index] }
                request = "https://"+self.ip_addrs[index]+":8443/rest/vpn/v1/tunnels" 
                response = requests.get(request, params=params_tunnels, headers=header, timeout=1, verify=False)
                resp = response.json()
                resp = resp.get("VPNTunnels")
                if resp is None:
                    continue
                for vpn in resp:
                    tunnels = []
                    tunnels.append(self.ip_addrs[index])
                    tunnels.append(self.api_tokens[index])
                    tunnels.append(self.fw_names[index])
                    tunnels.append(vpn['internal_name'])
                    tunnels.append(vpn['status'])
                    self.tunnel_list.append(tunnels)
            except requests.exceptions.RequestException as e:
                self.requestError(e)

    def requestError(self, e):
        """
        If an error occured during a request operation, it will be written in the logfile "requestError.log"
        """
        try:
            with open('requestError_restart.log', 'a') as f:
                now = datetime.now()
                dt_string = now.strftime("%Y-%m-%d %I:%M:%S,")
                txt = dt_string+str(e)
                f.write(txt+'\n')
                return
        except OSError:
            print("Could not open file requestError.log!")

    def restoreConnection(self):
        """ 
        Checks the Status of the VPN Tunnel and trys to re-initiate it with a POST command function.
        If the Status is down, the status will be logged in a logfile with the name "vpnconnections.log"
        """
        try:
            for vpn in self.tunnel_list:
                _ip, _token, _fw_name, _intern_name, _status = vpn 
                if _status.lower() == "down" or _status.lower() == "down (passive)": 
                    logging.warning(_fw_name+','+_intern_name+','+_status) 
                    self.restoreVpn(_ip, _token, _intern_name)
                if _status.lower() == "up":
                    logging.warning(_fw_name+','+_intern_name+','+_status) 
        except:
            print("Error occured while checking tunnel list")

    def restoreVpn(self, ip, token, name):
        """
            POST Command that trys to initiate a VPN Tunnel with REST API
        """
        try:
            params_init = { "tunnel": name, "envelope": True} 
            header = { "X-API-Token": token }
            request = "https://"+ip+":8443/rest/vpn/v1/tunnels/"+name+"/initiate" 
            response = requests.post(request, params=params_init, headers=header, verify=False)
        except requests.exceptions.RequestException as e:
            self.requestError(e)

    def getSingleData(self):
        for index in range(len(args.fw)):
            for i in range(len(self.fw_names)):
                if args.fw[index] == self.fw_names[i]:
                    listy = []
                    listy.append(self.ip_addrs[i])     
                    listy.append(self.fw_names[i])     
                    listy.append(self.api_tokens[i])
                    self.single_list.append(listy)
    
    def setRestoringData(self):
        self.clearList()
        for row in self.single_list:
            ip, fw, token = row
            self.ip_addrs.append(ip)
            self.fw_names.append(fw)
            self.api_tokens.append(token)

try:
    if args.fw:
        connect = connectionRestoring()
        connect.getIpAndToken()
        connect.getSingleData()
        connect.setRestoringData()
        connect.getVpnData()
        connect.restoreConnection()
    else:
        connect = connectionRestoring()
        connect.getIpAndToken()
        connect.getVpnData() 
        connect.restoreConnection()
except KeyboardInterrupt: 
    print("session closed")
