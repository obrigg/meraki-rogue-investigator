import time
import os
from meraki_sdk.meraki_sdk_client import MerakiSdkClient
from meraki_sdk.exceptions.api_exception import APIException
from pprint import pprint
import re

def SelectNetwork():
    # Fetch and select the organization
    print('\n\nFetching organizations...\n')
    organizations = meraki.organizations.get_organizations()
    ids = []
    print('{:<30} {:<20}'.format('ID: ', 'Name: '))
    print(50*"-")
    for organization in organizations:
        print('{:<30} {:<20}'.format(organization['id'],organization['name']))
        ids.append(organization['id'])
    selected = input('\nKindly select the organization ID you would like to query: ')
    if selected not in ids:
        raise Exception ('\nInvalid Organization ID')
    # Fetch and select the network within the organization
    print('\n\nFetching networks...\n')
    networks = meraki.networks.get_organization_networks({'organization_id': selected})
    ids = []
    print('{:<30} {:<20}'.format('ID: ', 'Name: '))
    print(50*"-")
    for network in networks:
        print('{:<30} {:<20}'.format(network['id'],network['name']))
        ids.append(network['id'])
    selected = input('\nKindly select the network ID you would like to query: ')
    if selected not in ids:
        raise Exception ('\nInvalid Network ID')
    return(selected)


if __name__ == '__main__':
    # Initializing Meraki SDK
    meraki = MerakiSdkClient(os.environ.get('MERAKI_KEY'))
    NETWORK_ID = SelectNetwork()
    userInput = ""
    rogues = meraki.networks.get_network_air_marshal({'network_id': NETWORK_ID})

    while userInput.lower() != "exit":
        userInput = input("Enter the BSSID you'd like to check... ")
        if userInput.lower == "exit":
            break
        if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", userInput.lower()):
            for rogue in rogues:
                highestListener = {'device': "", 'rssi': 0}
                for bssid in rogue['bssids']:
                    for detector in bssid['detectedBy']:
                        if detector['rssi'] > highestListener['rssi']:
                            highestListener = detector
                    if bssid['bssid'] == userInput.upper():
                        pprint(rogue)
                        print(f"""

                        Found the rogue!

                        SSID: {rogue['ssid']}
                        On channels: {rogue['channels']}
                        Closest AP: {highestListener['device']} with SNR of {highestListener['rssi']}
                        First seen: {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(rogue['firstSeen']))} UTC
                        Last seen: {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(rogue['lastSeen']))} UTC
                        """)

        else:
            print("Invalid MAC Address entered. Please try again or type 'exit' to quit")
