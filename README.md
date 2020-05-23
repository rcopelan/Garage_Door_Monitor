# Garage_Door_Monitor
Monitors openings and closings of a garage (or any type) door.  eMail addresses can be dynamically added in 
door_monitor.cfg [email] section without having to restart the program. 

## Installation
1. Install the necessary python libraries  
  `pip install -r requirements.txt`
2. rename the door_monitor.sample-cfg  to  door_monitor.cfg
3. Edit door_monitor.cfg to have parameters for your installation
2. Set the script file to run via crontab at reboot
3. Run the script file once at the command line OR reboot the computer  
`.\door_monitor.sh &`

## door_monitor.cfg format 
```
[email]    
email1     = option  

  
[smtp]  
smtp_server   = smtp.gmail.com   
smtp_port     = 587  
smtp_user     = user for the smtp server  
smtp_password = password for the smtp server  
  
[mqtt]  
broker_address = Broker IP address  
  
[sensor]  
door_pin = 23   #Pi GPIO pin for the door sensor  
  
[flags]  
debug_flag       = False  
send_to_Adafruit = True  
 
[aio]  
ADAFRUIT_IO_KEY = key for the Adafruit IO API  `
```
[email]  
email1:   valid email addresses to use for sending the message (note: can be an sms email address)  line can be prefixed with # to ignore
options: "both": sends message when door is opened & closed    "closed": only sends message when door is closed
Use 1 line per destination address

[smtp]    SMTP server parameters.  Self explanatory  

[mqtt] broker_address: server IP address or FQDN of the smtp server 
  
[sensor]  door_pin:   PI GPIO pin number for the switch on the door
  
[flags]   miscellaneous boolean flags  

[aio]   Key for the Adafruit IO API  

