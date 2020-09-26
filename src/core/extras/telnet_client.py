import sys
import telnetlib
import argparse
import time
import logging

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--dest_ip', dest="dest_ip", help='IP Address of the Destination node.',
        required=True)
    args = parser.parse_args()

    dest_ip = args.dest_ip
    username = "moses"
    password = "project_melody"

    tn = telnetlib.Telnet(dest_ip)
    tn.expect(["login: "])
    logging.info("Got login prompt")
    
    tn.write(username + "\n")

    if password :
        tn.expect(["Password: "])
        tn.write(password + "\n")

    logging.info("Sent password")
    

    i = 0
    while i < 2 :
        time.sleep(1)
        tn.write("echo \'Hello\'\n")
        logging.info("Sent Hello !")
        
        i = i + 1

    print (tn.read_very_eager())
    


if __name__ == "__main__":
    main()
