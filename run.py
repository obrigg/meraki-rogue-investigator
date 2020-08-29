import os, re, math
from datetime import datetime
from meraki_sdk.meraki_sdk_client import MerakiSdkClient
from meraki_sdk.exceptions.api_exception import APIException
from rich import print
from rich.console import Console
from rich.table import Table
from rich.progress import track

def SelectNetwork():
    # Fetch and select the organization
    print('\n\nFetching organizations...\n')
    organizations = meraki.organizations.get_organizations()
    ids = []
    table = Table(title="Meraki Organizations")
    table.add_column("Organization #", justify="left", style="cyan", no_wrap=True)
    table.add_column("Org Name", justify="left", style="cyan", no_wrap=True)
    counter = 0
    for organization in organizations:
        ids.append(organization['id'])
        table.add_row(str(counter), organization['name'])
        counter+=1
    console = Console()
    console.print(table)
    isOrgDone = False
    while isOrgDone == False:
        selected = input('\nKindly select the organization ID you would like to query: ')
        try:
            if int(selected) in range(0,counter):
                isOrgDone = True
            else:
                print('\t[bold red]Invalid Organization Number\n')
        except:
            print('\t[bold red]Invalid Organization Number\n')
    # Fetch and select the network within the organization
    print('\n\nFetching networks...\n')
    networks = meraki.networks.get_organization_networks({'organization_id': organizations[int(selected)]['id']})
    ids = []
    table = Table(title="Available Networks")
    table.add_column("Network #", justify="left", style="green", no_wrap=True)
    table.add_column("Network Name", justify="left", style="green", no_wrap=True)
    counter = 0
    for network in networks:
        ids.append(network['id'])
        table.add_row(str(counter), network['name'])
        counter += 1
    console = Console()
    console.print(table)
    isNetDone = False
    while isNetDone == False:
        selected = input('\nKindly select the Network you would like to query: ')
        try:
            if int(selected) in range(0,counter):
                isNetDone = True
            else:
                print('\t[bold red]Invalid Organization Number\n')
        except:
            print('\t[bold red]Invalid Organization Number\n')
    return(networks[int(selected)]['id'])

def SelectTimeFrame():
    isDone = False
    while isDone == False:
        timeFrame = input("\nSelect timeframe for the rogues (in hours - 1, 24 or All): ")
        if timeFrame.lower() in ['1', '24', 'all']:
            isDone = True
            return (timeFrame.upper())
        else:
            print("\t[bold red]Invalid input, please try again.\n")

def FilterRogues(allRogues, inventory, timeFrame, minimumRssi):
    # Timeframe filter
    if timeFrame == 'ALL':
        roguesInTime = allRogues
    else:
        roguesInTime = []
        for rogue in allRogues:
            delta = datetime.now() - datetime.fromtimestamp(rogue['lastSeen'])
            if delta.seconds < int(timeFrame)*60*60:
                roguesInTime.append(rogue)
    # RSSI Filter
    filteredRogues = []
    for rogue in roguesInTime:
        highestRssi = 0
        for bssid in rogue['bssids']:
            for observer in bssid['detectedBy']:
                if observer['rssi'] > highestRssi:
                    highestRssi = observer['rssi']
        if highestRssi >= minimumRssi:
            filteredRogues.append(rogue)
    # Convert serials to names
    for rogue in filteredRogues:
        for bssid in rogue['bssids']:
            for observer in bssid['detectedBy']:
                for device in inventory:
                    if device['serial'] == observer['device']:
                        observer['name'] = device['name']
    return(filteredRogues)

def DisplayRogues(rogues, timeFrame):
    pages = math.ceil(len(rogues)/roguesPerPage)
    for page in range(pages):
        table = Table(title="Rogue SSID List")
        table.add_column("SSID", justify="left", style="green", no_wrap=True)
        table.add_column("# of APs", justify="left", style="green", no_wrap=True)
        table.add_column("Last Seen", justify="left", style="green", no_wrap=True)
        table.add_column("Age (days)", justify="left", style="green", no_wrap=True)
        for i in range(roguesPerPage*page, roguesPerPage*(page+1)):
            try:
                days = (datetime.now() - datetime.fromtimestamp(rogues[i]['firstSeen'])).days
                table.add_row(rogues[i]['ssid'], str(len(rogues[i]['bssids'])), 
                    str(datetime.fromtimestamp(rogues[i]['lastSeen'])), str(days))
            except:
                continue
        console = Console()
        console.print(table)
        print(f'Page {page + 1} of {pages}.')
        if input("Press ENTER to continue, or 'quit' to quit.\n").lower() == 'quit':
            break

def CheckRogue(rogues, userInput):
    isFound = False
    if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", userInput.lower()):
        for rogue in rogues:
            for bssid in rogue['bssids']:
                if bssid['bssid'] == userInput.upper():
                    isFound = True
                    PrintBSSID(rogue, userInput)
    else:
        for rogue in rogues:
            if rogue['ssid'] == userInput:
                isFound = True
                PrintSSID(rogue)
    if not isFound:
        print("\n[red]Invalid MAC Address or SSID entered[/red]. Please try entering a SSID/BSSID, 'display' to display the list of SSIDs or type 'quit' to quit")

def PrintSSID(rogue):
    table = Table(title="Rogue SSID Details")
    table.add_column("Last Seen", justify="left", style="green", no_wrap=True)
    table.add_column("Age (days)", justify="left", style="green", no_wrap=True)
    table.add_column("# of APs", justify="center", style="cyan", no_wrap=True)
    table.add_column("Channels", justify="center", style="cyan", no_wrap=True)
    #
    days = (datetime.now() - datetime.fromtimestamp(rogue['firstSeen'])).days
    table.add_row(str(datetime.fromtimestamp(rogue['lastSeen'])), str(days), str(len(rogue['bssids'])), 
        str(rogue['channels']))
    console = Console()
    console.print(table)
    for bssid in rogue['bssids']:
        PrintBSSID(rogue, bssid['bssid'])

def PrintBSSID(rogue, bssid):
    print(f'\n\tReport for BSSID [blue]{bssid}\n')
    table = Table(title="Rogue BSSID Details")
    table.add_column("SSID", justify="left", style="cyan", no_wrap=True)
    table.add_column("Channels", justify="center", style="cyan", no_wrap=True)
    table.add_column("Last seen", justify="left", style="cyan", no_wrap=True)
    table.add_column("Age (days)", justify="left", style="green", no_wrap=True)
    days = (datetime.now() - datetime.fromtimestamp(rogue['firstSeen'])).days
    table.add_row(rogue['ssid'], str(rogue['channels']), 
        str(datetime.fromtimestamp(rogue['lastSeen'])), str(days))
    console = Console()
    console.print(table)
    print()
    table = Table(title="Observing APs")
    table.add_column("Meraki AP Name", justify="left", style="cyan", no_wrap=True)
    table.add_column("Meraki AP Serial", justify="left", style="cyan", no_wrap=True)
    table.add_column("SNR", justify="center", style="cyan", no_wrap=True)
    for rogueBssid in rogue['bssids']:
        for observer in rogueBssid['detectedBy']:
            if rogueBssid['bssid'] == bssid:
                table.add_row(observer['name'], observer['device'], str(observer['rssi']))        
    console = Console()
    console.print(table)

if __name__ == '__main__':
    # User defind variables
    roguesPerPage = 20
    minimumRssi = 1
    # Initializing Meraki SDK
    meraki = MerakiSdkClient(os.environ.get('MERAKI_KEY'))
    NETWORK_ID = SelectNetwork()
    timeFrame = SelectTimeFrame()
    userInput = ""
    rogues = []
    inventory = meraki.devices.get_network_devices(NETWORK_ID)
    allRogues = meraki.networks.get_network_air_marshal({'network_id': NETWORK_ID})
    filteredRogues = FilterRogues(allRogues, inventory, timeFrame, minimumRssi)

    while userInput.lower() != "quit":
        print("""\n[green]What would you like to do? Your options are:
    * Enter a SSID you'd like to investigate.
    * Enter a BSSID you'd like to investigate.
    * Enter 'display' to display a list of detected rogue SSIDs.
    * Enter 'quit' to exit the program.\n""")
        userInput = input("\t")
        if userInput == "":
            pass
        elif userInput.lower() == "display":
            DisplayRogues(filteredRogues, timeFrame)
        elif userInput.lower() != "quit":
            CheckRogue(filteredRogues, userInput)
        else:
            print('Quiting...\n')
        userInput = ""