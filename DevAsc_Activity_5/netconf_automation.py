import sys
from ncclient import manager
import requests
import json

# --- CONFIGURATION VARIABLES ---
ROUTER = {
    "host": "ios-xe-mgmt.cisco.com", # Replace with your router IP/Sandbox
    "port": 830,
    "username": "developer",         # Replace with your username
    "password": "C1sco12345",        # Replace with your password
    "hostkey_verify": False
}

WEBEX_TOKEN = "NzZlNWVkZWMtNjI0NC00MDM2LTk0YjctM2Y3NTg2ZjE4YzVkYTlkYmU4YzMtNzk4_P0A1_6dc8d78d-8b30-4860-a0cf-2c9415a40317"
WEBEX_ROOM_ID = "6dc8d78d-8b30-4860-a0cf-2c9415a40317"

# --- YANG MODEL / NETCONF XML PAYLOAD ---
# We use the ietf-interfaces YANG model structure for compatibility.
# This XML payload performs the 3 required changes.
config_payload = """
<config>
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface>
      <name>GigabitEthernet1</name>
      <description>Configured by Python Automation - Change 1</description>
    </interface>
    
    <interface>
      <name>Loopback0</name>
      <description>Main Loopback - Change 2</description>
    </interface>
    
    <interface>
      <name>Loopback100</name>
      <description>New Automation Interface - Change 3</description>
      <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
      <enabled>true</enabled>
      <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
        <address>
          <ip>192.168.100.1</ip>
          <netmask>255.255.255.0</netmask>
        </address>
      </ipv4>
    </interface>
  </interfaces>
</config>
"""

# --- FUNCTIONS ---

def get_running_config(m):
    """Retrieves specific interface config to verify changes."""
    print("\n[+] Retrieving current Running-Config...")
    # We filter only for interfaces to keep output readable
    filter_xml = """
    <filter>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface></interface>
      </interfaces>
    </filter>
    """
    data = m.get_config(source='running', filter=filter_xml)
    return data.xml

def send_webex_notification(status_message):
    """Sends a message to Webex Teams."""
    print(f"\n[+] Sending Webex Notification: {status_message}")
    url = "https://webexapis.com/v1/messages"
    headers = {
        "Authorization": f"Bearer {WEBEX_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "roomId": WEBEX_ROOM_ID,
        "text": status_message
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        print("    Success! Message sent.")
    except Exception as e:
        print(f"    Failed to send Webex message: {e}")

# --- MAIN EXECUTION ---

def main():
    try:
        # 1. Connect to Router via NETCONF
        print(f"Connecting to {ROUTER['host']}...")
        with manager.connect(**ROUTER) as m:
            
            # 2. Verify current running-config (BEFORE)
            print("--- CONFIG BEFORE CHANGES ---")
            print(get_running_config(m))
            
            # 3. Make three changes to the configuration
            print("\n[+] Applying 3 changes via NETCONF...")
            netconf_reply = m.edit_config(target='running', config=config_payload)
            print(f"    Transaction Status: {netconf_reply.ok}")
            
            # 4. Verify the changes (AFTER)
            print("\n--- CONFIG AFTER CHANGES ---")
            new_config = get_running_config(m)
            print(new_config)
            
            # 5. Send Notification
            if netconf_reply.ok:
                msg = "SUCCESS: Network Automation Job 8.6.9 complete. 3 Interface changes applied to Router."
                send_webex_notification(msg)
            else:
                send_webex_notification("FAILURE: Automation script ran but returned errors.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
