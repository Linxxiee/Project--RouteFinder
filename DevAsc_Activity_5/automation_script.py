import requests
from ncclient import manager
import sys
import getpass

# -----------------------------------------------------------------------------
# PART 1: WEBEX CONFIGURATION
# -----------------------------------------------------------------------------
# Paste your Webex Token and Room ID here
WEBEX_ACCESS_TOKEN = "Bearer MTNlYzA5NTUtMDM3Ni00MzJjLWE0NDQtZWMzMDhiYjM5OGE0MTY1ZTE3MWQtYTlj_P0A1_87d6b4a4-0254-4c7e-8cf0-2917b2d84a0f"
WEBEX_ROOM_ID = "768a6630-d44c-11f0-b4b4-7d4368f2cdc8"
WEBEX_URL = "https://webexapis.com/v1/messages"

# -----------------------------------------------------------------------------
# PART 2: THE REAL CONFIGURATION (Loopback)
# -----------------------------------------------------------------------------
config_payload = """
<config>
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface>
      <name>Loopback101</name>
      <description>Automated_Interface_Created_by_Python</description>
      <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
      <enabled>true</enabled>
      <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
        <address>
          <ip>10.10.10.101</ip>
          <netmask>255.255.255.255</netmask>
        </address>
      </ipv4>
    </interface>
  </interfaces>
</config>
"""

# -----------------------------------------------------------------------------
# PART 3: MAIN EXECUTION
# -----------------------------------------------------------------------------
def run_real_automation():
    print("\n--- CISCO SANDBOX CONNECTION ---")
    print("Please enter the credentials from the DevNet Sandbox Portal.")
    
    # 1. GET CREDENTIALS FROM USER
    host_input = input("Router Host (e.g., sandbox-iosxe-latest-1.cisco.com): ") or "sandbox-iosxe-latest-1.cisco.com"
    user_input = input("Router Username (usually 'developer' or 'admin'): ") or "developer"
    pass_input = input("Router Password (copy from website): ")

    print(f"\nConnecting to {host_input}...")

    try:
        # 2. CONNECT TO ROUTER
        # We use look_for_keys=False to stop your computer's SSH keys from breaking the login
        with manager.connect(host=host_input,
                             port=830,
                             username=user_input,
                             password=pass_input,
                             hostkey_verify=False,
                             look_for_keys=False,
                             allow_agent=False,
                             device_params={'name': 'iosxe'}) as m:
            
            print(" >>> CONNECTION SUCCESSFUL!")
            
            # 3. PUSH CONFIG
            print("Pushing configuration...")
            try:
                m.edit_config(target='running', config=config_payload)
                print("Configuration Applied Successfully.")
            except Exception as e:
                print(f"Config Warning (Loopback might already exist): {e}")

            # 4. SEND WEBEX NOTIFICATION
            send_webex_notification(f"SUCCESS: Real Python Automation connected to {host_input}!")

    except Exception as e:
        print(f"\n[X] CONNECTION FAILED: {e}")
        print("Tip: If you see 'Authentication failed', your password from the portal is wrong or expired.")

# -----------------------------------------------------------------------------
# WEBEX FUNCTION
# -----------------------------------------------------------------------------
def send_webex_notification(message_text):
    print(f"--- Sending Webex Notification ---")
    headers = {"Authorization": WEBEX_ACCESS_TOKEN, "Content-Type": "application/json"}
    body = {"roomId": WEBEX_ROOM_ID, "text": message_text}
    
    try:
        response = requests.post(WEBEX_URL, headers=headers, json=body)
        if response.status_code == 200:
            print("Webex message sent.")
        else:
            print(f"Webex Failed: {response.status_code}")
    except Exception as e:
        print(f"Webex Error: {e}")

if __name__ == '__main__':
    run_real_automation()