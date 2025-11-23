#!/bin/bash
# Script: check_setup.sh
# Description: Gathers essential system configuration and component status
#              for the Cowrie, Docker, ZeroTier, and Fail2ban environment.

echo "======================================================"
echo " Cowrie Honeypot Environment Snapshot"
echo " Generated on: $(date)"
echo " OS: $(uname -a)"
echo "------------------------------------------------------"

# --- 1. System Dependency Checks ---
echo "[1] CORE DEPENDENCY VERSIONS"
echo "------------------------------------------------------"
echo -n "Bash Version: " && bash --version | head -n 1
echo -n "Python3 Version: " && python3 --version
command -v docker >/dev/null 2>&1 && echo -n "Docker Version: " && docker --version
command -v docker-compose >/dev/null 2>&1 && echo -n "Docker Compose Version: " && docker-compose --version
command -v zerotier-cli >/dev/null 2>&1 && echo -n "ZeroTier-CLI Version: " && zerotier-cli -v
command -v fail2ban-client >/dev/null 2>&1 && echo -n "Fail2ban Version: " && fail2ban-client --version | grep "Fail2ban "

echo -e "\n[2] NETWORK (ZeroTier) STATUS"
echo "------------------------------------------------------"
command -v zerotier-cli >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "ZeroTier Status:"
    zerotier-cli status

    echo -e "\nZeroTier Network Membership (ID: 0000...):"
    zerotier-cli listnetworks | awk '$2!="OK" || $3!="REQUESTING_CONFIG" {print "ID: "$1, "Status: "$3, "IPs: "$NF}'
    echo "Note: The correct ZeroTier network IP should not be 0.0.0.0."
else
    echo "ZeroTier-CLI not found. Skip network status check."
fi


echo -e "\n[3] DOCKER CONTAINER AND NETWORK STATUS"
echo "------------------------------------------------------"
if command -v docker >/dev/null 2>&1; then
    echo "Active Cowrie Container(s):"
    docker ps --filter "name=cowrie" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Networks}}"
    
    echo -e "\nCowrie Docker Network Configuration:"
    # Use a filter if you have a specific network name, otherwise show all
    # Replace 'my_cowrie_net' with your actual network name if you used one
    docker network ls --filter driver=bridge --format "table {{.Name}}\t{{.Driver}}\t{{.ID}}"

    echo -e "\nCowrie Volume Mount Check (Configuration/Logs):"
    # Assuming your docker-compose mounts a local directory named 'cowrie'
    if [ -d "./cowrie/etc" ] && [ -d "./cowrie/log" ]; then
        echo "  - Configuration directory found: ./cowrie/etc"
        echo "  - Log directory found: ./cowrie/log (JSON log should be here)"
    else
        echo "  - WARNING: Expected local 'cowrie/etc' or 'cowrie/log' directories not found in the current path."
    fi

else
    echo "Docker not found. Skip container status checks."
fi


echo -e "\n[4] FAIL2BAN SETUP AND JAIL CHECKS"
echo "------------------------------------------------------"
if command -v fail2ban-client >/dev/null 2>&1; then
    echo "Fail2ban Running Status:"
    fail2ban-client status
    
    echo -e "\nActive Jails:"
    fail2ban-client status | grep "Jail list" | sed 's/Jail list://g' | sed 's/, / /g'
    
    # Check for the cowrie jail specifically
    if fail2ban-client status | grep -q "cowrie"; then
        echo -e "\nCowrie Jail Status:"
        fail2ban-client status cowrie
    else
        echo "Cowrie jail does not appear to be active or named 'cowrie'."
    fi
else
    echo "Fail2ban-client not found. Skip Fail2ban checks."
fi

echo -e "\n======================================================"
echo " Setup Check Complete."
echo "======================================================"
