#!/usr/bin/env python3
"""
Cowrie Honeypot Log Analyzer and Visualizer
Generates statistics and charts from attack logs
"""

import re
from collections import Counter
import matplotlib.pyplot as plt
import os

LOG_FILE = "logs/cowrie.log"
OUTPUT_DIR = "docs/screenshots"

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_logs():
    """Extract attack data from logs"""
    passwords = []
    usernames = []
    ips = []
    
    print("📖 Reading logs...")
    with open(LOG_FILE, 'r', errors='ignore') as f:
        for line in f:
            # Extract login attempts
            if "login attempt" in line:
                match = re.search(r"login attempt \[b'(.*?)'/b'(.*?)'\]", line)
                if match:
                    usernames.append(match.group(1))
                    passwords.append(match.group(2))
            
            # Extract IPs
            if "New connection" in line:
                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+):\d+', line)
                if ip_match:
                    ips.append(ip_match.group(1))
    
    return usernames, passwords, ips

def print_statistics(usernames, passwords, ips):
    """Print text statistics"""
    print("\n" + "="*50)
    print("  HONEYPOT ATTACK STATISTICS")
    print("="*50 + "\n")
    
    print(f"Total login attempts: {len(usernames)}")
    print(f"Unique attacker IPs: {len(set(ips))}")
    print(f"Unique usernames tried: {len(set(usernames))}")
    print(f"Unique passwords tried: {len(set(passwords))}")
    
    print("\n Top 5 Passwords:")
    for pwd, count in Counter(passwords).most_common(5):
        print(f"   {count:2d} - {pwd if pwd else '(empty)'}")
    
    print("\n Top 5 Usernames:")
    for user, count in Counter(usernames).most_common(5):
        print(f"   {count:2d} - {user}")
    
    print("\nAttacker IPs:")
    for ip in set(ips):
        print(f"   • {ip}")
    print()

def create_charts(usernames, passwords):
    """Generate visualization charts"""
    print("Generating charts...\n")
    
    # Chart 1: Top Passwords
    if passwords:
        plt.figure(figsize=(10, 6))
        top_pass = Counter(passwords).most_common(8)
        labels = [p if p else "(empty)" for p, _ in top_pass]
        counts = [c for _, c in top_pass]
        
        plt.barh(labels, counts, color='#e74c3c')
        plt.xlabel('Number of Attempts', fontsize=12)
        plt.title('Top Passwords Attempted', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        output_file = f'{OUTPUT_DIR}/chart-passwords.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"✓ Created: {output_file}")
        plt.close()
    
    # Chart 2: Top Usernames
    if usernames:
        plt.figure(figsize=(10, 6))
        top_users = Counter(usernames).most_common(8)
        labels = [u for u, _ in top_users]
        counts = [c for _, c in top_users]
        
        plt.barh(labels, counts, color='#3498db')
        plt.xlabel('Number of Attempts', fontsize=12)
        plt.title('Top Usernames Attempted', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        output_file = f'{OUTPUT_DIR}/chart-usernames.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"✓ Created: {output_file}")
        plt.close()
    
    # Chart 3: Summary Dashboard
    plt.figure(figsize=(12, 8))
    
    # Subplot 1: Passwords
    plt.subplot(2, 2, 1)
    top_pass = Counter(passwords).most_common(5)
    labels = [p[:15] if p else "(empty)" for p, _ in top_pass]
    counts = [c for _, c in top_pass]
    plt.bar(range(len(labels)), counts, color='#e74c3c')
    plt.xticks(range(len(labels)), labels, rotation=45, ha='right')
    plt.ylabel('Attempts')
    plt.title('Top 5 Passwords')
    plt.grid(axis='y', alpha=0.3)
    
    # Subplot 2: Usernames
    plt.subplot(2, 2, 2)
    top_users = Counter(usernames).most_common(5)
    labels = [u for u, _ in top_users]
    counts = [c for _, c in top_users]
    plt.bar(range(len(labels)), counts, color='#3498db')
    plt.xticks(range(len(labels)), labels, rotation=45, ha='right')
    plt.ylabel('Attempts')
    plt.title('Top 5 Usernames')
    plt.grid(axis='y', alpha=0.3)
    
    # Subplot 3: Summary Stats (as text)
    plt.subplot(2, 1, 2)
    plt.axis('off')
    summary_text = f"""
    ATTACK SUMMARY
    
    Total Login Attempts: {len(usernames)}
    Unique Passwords: {len(set(passwords))}
    Unique Usernames: {len(set(usernames))}
    
    Most Common Password: {Counter(passwords).most_common(1)[0][0] if passwords else 'N/A'}
    Most Common Username: {Counter(usernames).most_common(1)[0][0] if usernames else 'N/A'}
    """
    plt.text(0.1, 0.5, summary_text, fontsize=14, family='monospace',
             verticalalignment='center')
    
    plt.suptitle('Honeypot Attack Analysis Dashboard', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    output_file = f'{OUTPUT_DIR}/dashboard.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Created: {output_file}")
    plt.close()

def main():
    print("\n Cowrie Honeypot Log Analyzer")
    print("="*50 + "\n")
    
    # Check if log file exists
    if not os.path.exists(LOG_FILE):
        print(f"❌ Error: Log file not found: {LOG_FILE}")
        return
    
    # Parse logs
    usernames, passwords, ips = parse_logs()
    
    if not usernames:
        print("❌ No attack data found in logs!")
        return
    
    # Print statistics
    print_statistics(usernames, passwords, ips)
    
    # Create charts
    create_charts(usernames, passwords)
    
    print("\n" + "="*50)
    print("✅ Analysis complete!")
    print(f" Charts saved to: {OUTPUT_DIR}/")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
