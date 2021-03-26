# vpn_reconnect_barracuda

File: cc_infos.py:
      Requires a File with IP Address of CC-FW and an API Token
      Format of File: fwname,token

File: restart.py
      checks the firewalls that where found from the cc firewall
      requires to add api tokens to all firewalls by hand
      checks the state of all vpn connections and restart if the state is down/down(disabled)

File: send_mail.py
      sends an email, initial is smtp written for cablelink salzburg
      requires a txt with user data
      format: Sender Email
              PW
              Receiver Email



