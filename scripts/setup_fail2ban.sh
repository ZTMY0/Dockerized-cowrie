#!/bin/bash
# Script: setup_fail2ban.sh
# Description: Automates the installation of Fail2ban and configures it to
#              monitor Cowrie logs for brute-force attacks and send email alerts.
#
# Prerequisite: This script assumes you are running it from the directory
#               that contains your 'config/logs' directory.

# =========================================================================
# ⚠️ USER-CONFIGURABLE VARIABLES ⚠️
# =========================================================================
# 1. The local path where cowrie.json is saved by Docker (relative to this script's location)
COWRIE_LOG_PATH="/home/ihab/Desktop/simple-honeypot-project/config/logs/cowrie.json"

# 2. Your email address for notification
DEST_EMAIL="ihab.zaghdane@eidia.ueuromed.org" # <-- REPLACE THIS WITH YOUR REAL EMAIL

# 3. Email provider for the 'sender' of the email (e.g., mailer@honeypot.com)
SENDER_EMAIL="cowrie-alert@test.local"
# =========================================================================

echo "========================================================="
echo " AUTOMATED FAIL2BAN & COWRIE ALERT SETUP"
echo " Target Log: $COWRIE_LOG_PATH"
echo " Alert Email: $DEST_EMAIL"
echo "========================================================="

# --- 1. Install Fail2ban and Sendmail (for Email Notifications) ---
echo -e "\n[1/5] Installing Fail2ban and Sendmail/Postfix..."
# Adding -y for non-interactive install
sudo apt update
sudo apt install -y fail2ban postfix mailutils

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install required packages. Exiting."
    exit 1
fi
echo "Installation complete."

# --- 2. Create Custom Cowrie Filter File for Fail2ban ---
# This filter tells Fail2ban what to look for in the logs.
echo -e "\n[2/5] Creating Fail2ban filter for Cowrie..."
# Fixing the here-doc syntax by ensuring 'EOF' is not indented
sudo bash -c "cat > /etc/fail2ban/filter.d/cowrie.conf << EOF
[Definition]
failregex = .*login.failed.*username=.*password=.*src_ip='<HOST>'.*
ignoreregex = 
# Cowrie uses JSON logs, so we MUST specify the log format
logpath = /invalid/path/ (Overridden by jail.local)
logtype = json
# Ensure the backend is set to the aggressive 'polling' method for safety
backend = polling
EOF"
echo "Cowrie filter created at /etc/fail2ban/filter.d/cowrie.conf"


# --- 3. Create Custom Jail Configuration ---
# This jail links the filter to an action (banning and emailing)
echo -e "\n[3/5] Creating Fail2ban jail configuration..."
# Fixing the here-doc syntax by ensuring 'EOF' is not indented
sudo bash -c "cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
# Default action: ban the IP then notify the email
banaction = iptables-multiport
action = %(banaction)s[name=%(__name__)s, port=\"ssh\", protocol=%(protocol)s]
         %(action_mw)s

# Monitor time (ban time: 1 hour)
bantime  = 3600

# Find time (5 failures within 10 minutes)
findtime = 600

# Max failures
maxretry = 5

# Set up the mail action
mta = sendmail # Use sendmail for simplicity
dest = $DEST_EMAIL 
sender = $SENDER_EMAIL
sendername = Cowrie-Honeypot-Alert

[cowrie]
enabled  = true
port     = 2222,ssh
filter   = cowrie
logpath  = $COWRIE_LOG_PATH
maxretry = 5
EOF"

# --- 4. Restart services and Set Permissions ---
echo -e "\n[4/5] Enabling and restarting Fail2ban service..."
# Setting read permission for root so Fail2ban can read the custom log path
sudo chown root:adm $COWRIE_LOG_PATH 2>/dev/null 
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban
sudo systemctl status fail2ban | grep "Active"

# --- 5. Final Verification ---
echo -e "\n[5/5] Checking Cowrie Jail Status..."
# Gives Fail2ban a moment to load the jail
sleep 5 
sudo fail2ban-client status cowrie

echo -e "\n========================================================="
echo " SETUP COMPLETE."
echo " 1. Fail2ban is successfully configured and running."
echo " 2. An email will be sent to $DEST_EMAIL after 5 failed login attempts in 10 minutes."
echo " 3. Test the setup immediately with 5 failed SSH login attempts."
echo "========================================================="
