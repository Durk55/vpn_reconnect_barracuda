import requests
import json
import urllib3
from requests.auth import HTTPBasicAuth
urllib3.disable_warnings()

class cc_Infos():
    """
    This Class connects to the CC-Barracuda Firewall with IP and Token from a file called "ccinfos.txt")
    The Script send a request to get all ranges, clusters and then all firewalls connected with the cc firewall.
    If not already exists the IP and the FW Name are written in a file called "fwlist.txt"
    """ 
    def __init__(self):
        self.range_list = []
        self.cluster_list = []
        self.cc_ip = ""
        self.cc_token = ""
        self.ip_name_list = []

    def getTokenAndIp(self):
        """
        Gets the IP Address of the CC Firewall and the REST-API Token from a file called "ccinfos.txt"
        Optional(DE): Villeicht die IP und den Token der CC Firewall als argument uebergeben
        """
        try:
            with open('ccinfos.txt', 'r') as f:
                for lines in f.readlines():
                    ip, token = lines.split(',')
                    self.cc_ip = ip
                    self.cc_token = token.rstrip('\n')
        except OSError:
            print("Could not open file ccinfos.txt!")

    def getRanges(self):
        """
        Gets the avaliable Ranges from the CC Firewall and saves them in a List
        """
        try:
            params = { "expand": False, "envelope": True, "X-API-Token": self.cc_token }
            request = "https://"+self.cc_ip+":8443/rest/cc/v1/ranges"
            response = requests.get(request, params=params, auth=HTTPBasicAuth('root', 'ngf1r3wall'), verify=False)
            resp = response.json()
            resp = resp.get("ranges")
            for ranges in resp:
                self.range_list.append(ranges)
        except requests.exceptions.RequestException as e:
            self.requestError(e)
 
    def getCluster(self):
        """
        Gets the avaliable Clusters from the CC Firewall and saves them in a List
        """
        try:
            for index in range(len(self.range_list)):
                params = { "expand": False, "range": self.range_list[index] , "envelope": True, "X-API-Token": self.cc_token }
            request = "https://"+self.cc_ip+":8443/rest/cc/v1/ranges/"+str(self.range_list[index])+"/clusters"
            response = requests.get(request, params=params, auth=HTTPBasicAuth('root', 'ngf1r3wall'), verify=False)
            resp = response.json()
            resp = resp.get("clusters")
            for clusters in resp:
                self.cluster_list.append(clusters)
        except requests.exceptions.RequestException as e:
            self.requestError(e)

    def getBoxes(self):
        """
        Gets all avaliable Boxes from the CC Firewall and saves the name and the IP Address in two seperate lists
        """
        try:
            for index in range(len(self.range_list)):
                for cluster_index in range(len(self.cluster_list)):
                    params = { "expand": 1, "cluster": self.cluster_list[cluster_index] ,"range": self.range_list[index], "envelope": True, "X-API-Token": self.cc_token }
                    request = "https://"+self.cc_ip+":8443/rest/cc/v1/ranges/"+str(self.range_list[index])+"/clusters/"+self.cluster_list[cluster_index]+"/boxes"
                    response = requests.get(request, params=params, auth=HTTPBasicAuth('root', 'ngf1r3wall'), verify=False)
                    if response.status_code == 404:
                        continue
                    resp = response.json()
                    resp = resp.get("boxes")
                    for box in resp:    
                        ip = box.get("ip")
                        name = box.get("name")
                        self.ip_name_list.append(ip+','+name+',')
        except requests.exceptions.RequestException as e:
            self.requestError(e) 

    def checkString(self, line):
        """
        Checks if a String already exists in the file "fwlist.txt"
        """
        try:
            with open("fwlist.txt", "r") as fw_list:
                if line in fw_list.read():
                    return True
                else:
                    return False
        except OSError:
            print("could not open file fwlist.txt!")

    def checkFile(self):
        """
        Checks the file and append a string if it doesnt exist already
        """
        try:
            with open("fwlist.txt", "a") as fw_list:
                for line in self.ip_name_list:
                    if self.checkString(line):
                        continue
                    else:
                        fw_list.write(line+'\n')
        except OSError:
            print("Could not open file fwlist.txt!")

    def requestError(self, e):
        try:
            with open('requestError.log', 'a') as f:
                now = datetime.now()
                dt_string = now.strftime("%Y-%m-%d %I:%M:%S")
                txt = dt_string+str(e)
                f.write(txt+'\n')
        except OSError:
            print("Could not open file reqeustError.log")

x = cc_Infos()
x.getTokenAndIp()
x.getRanges()
x.getCluster()
x.getBoxes()
x.checkFile()
