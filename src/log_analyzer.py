import streamlit as st
import pandas as pd
import re
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="Cowrie Log Forensics", layout="wide")
st.title(" Cowrie Honeypot: Raw Log Analysis")
st.markdown("Generating structured intelligence from unstructured `cowrie.log` data.")

# --- PARSING FUNCTION (The Portfolio "Flex") ---
@st.cache_data
def parse_cowrie_log(file_path):
    data = []
    
    # Regex patterns to extract data from the raw text
    # Pattern for basic connection info
    ip_pattern = re.compile(r"New connection: ([\d\.]+):")
    # Pattern for login attempts: [root/123456]
    login_pattern = re.compile(r"login attempt \[(.*)/(.*)\] (.*)")
    # Pattern for commands: CMD: ls -la
    cmd_pattern = re.compile(r"CMD: (.*)")
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                timestamp = line[:23] # Extract roughly the first 23 chars for time
                
                # 1. Check for Login Attempts
                login_match = login_pattern.search(line)
                if login_match:
                    data.append({
                        "timestamp": timestamp,
                        "type": "Login Attempt",
                        "src_ip": "Unknown (Session Linked)", # Text logs make mapping IP to every line hard without session ID logic, this is simplified
                        "user": login_match.group(1),
                        "password": login_match.group(2),
                        "status": login_match.group(3), # succeeded or failed
                        "command": None
                    })
                    continue

                # 2. Check for Commands (Post-Compromise)
                cmd_match = cmd_pattern.search(line)
                if cmd_match:
                    data.append({
                        "timestamp": timestamp,
                        "type": "Command Execution",
                        "src_ip": "Unknown (Session Linked)",
                        "user": None,
                        "password": None,
                        "status": None,
                        "command": cmd_match.group(1)
                    })
                    continue
                    
                # 3. Check for Connections (to get IPs)
                # Note: In text logs, IPs appear on the "New connection" line. 
                # For a simple dashboard, we extract all unique IPs found in the logs.
                ip_match = ip_pattern.search(line)
                if ip_match:
                     data.append({
                        "timestamp": timestamp,
                        "type": "New Connection",
                        "src_ip": ip_match.group(1),
                        "user": None,
                        "password": None,
                        "status": None,
                        "command": None
                    })

        return pd.DataFrame(data)
    except FileNotFoundError:
        st.error(f"Could not find file: {file_path}")
        return pd.DataFrame()

# --- LOAD DATA ---
# CHANGE THIS path if your file is in a subfolder
df = parse_cowrie_log("logs/cowrie.log") 

if not df.empty:
    # --- METRICS ROW ---
    col1, col2, col3 = st.columns(3)
    
    # Calculate metrics
    total_conns = df[df['type'] == "New Connection"].shape[0]
    unique_ips = df[df['type'] == "New Connection"]['src_ip'].nunique()
    cmds_executed = df[df['type'] == "Command Execution"].shape[0]
    
    col1.metric("Total Connections", total_conns)
    col2.metric("Unique Attacker IPs", unique_ips)
    col3.metric("Commands Executed", cmds_executed)

    st.divider()

    # --- BRUTE FORCE ANALYSIS ---
    c1, c2 = st.columns(2)
    
    # Filter for logins
    logins = df[df['type'] == "Login Attempt"]
    
    if not logins.empty:
        with c1:
            st.subheader("Top Attacked Usernames")
            top_users = logins['user'].value_counts().head(10)
            st.bar_chart(top_users)
            
        with c2:
            st.subheader("Top Passwords Tried")
            top_pass = logins['password'].value_counts().head(10)
            st.bar_chart(top_pass)
    else:
        st.info("No login attempts found in logs yet.")

    # --- ATTACKER ACTIVITY (COMMANDS) ---
    st.divider()
    st.subheader("Attacker Activity (Commands Executed)")
    st.caption("This table shows what the attacker did after gaining access.")
    
    commands = df[df['type'] == "Command Execution"][['timestamp', 'command']]
    
    if not commands.empty:
        st.table(commands)
    else:
        st.success("No commands executed (Attacker may have failed to login).")

    # --- IP LIST ---
    st.divider()
    with st.expander("View All Attacker IPs"):
        ips = df[df['type'] == "New Connection"]['src_ip'].value_counts()
        st.dataframe(ips)

else:
    st.warning("Please verify 'cowrie.log' is in the directory.")
