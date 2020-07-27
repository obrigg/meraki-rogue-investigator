# Meraki Rogue Investigator

### The Challenge

The Meraki dashboard is amazing, but (at the moment) locating rogue APs and SSIDs is not very user-friendly.
The dashboard aggregates BSSIDs under the same SSID making it hard to get an idea for the location of each BSSID.

### The Solution

This script will use the Meraki API to query all rogue BSSIDs on a given Meraki network, and return detailed information for any given BSSID.

### How to run the script

You'll need to store the Meraki dashboard API key as an environment variable:
`export MERAKI_KEY = <YOUR MERAKI API KEY>`
and install the Meraki SDK via `pip install -r requirements.txt`

Now you're ready. Good luck!
`python run.py`


----
### Licensing info
Copyright (c) 2020 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
