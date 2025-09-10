# ![Typing SVG](https://readme-typing-svg.demolab.com?font=bungee&duration=4000&pause=100&color=F75542&width=435&lines=CoreView;System+%26+Security+Information+Tool)
**~~simplinfo~~** **CoreView** is a terminal-based Linux utility. It provides a <<**concise**>> overview of system and security information ___[with some extras]___ while highlighting potential risks.

**Version 1.0**
<img width="1907" height="357" alt="image" src="https://github.com/user-attachments/assets/879339d2-5bb3-4821-b888-6e2999b900ba" />
**Version 2.1**
<img width="1920" height="782" alt="2025-08-30_03-56" src="https://github.com/user-attachments/assets/eb62c877-49f6-4c52-9967-6d09cbcf1cc7" />

## Features

- **Internal & External IPs** – Hostname, local IP, public IP.  
- **System Info** – OS, release, version, architecture.  
- **User Management** – Logged-in users, all users, current user; alerts on unexpected root accounts.  
- **Processes & Performance** – Top 5 CPU-consuming processes.  
- **Network Exposure** – Open TCP/UDP ports; warns if accessible from any network.  
- **SUID/SGID Files** – Detects files with elevated permissions.  
- **World-Writable Directories** – Identifies directories writable by any user.  
- **Cron Jobs** – Lists scheduled tasks.  
- **Firewall Status** – Checks UFW; warns if inactive.  
- **SSH Logins** – Displays recent attempts and failed logins.  
- **Kernel Version** – Shows current kernel; warns if outdated or generic.  
- **Security Hints** – Actionable suggestions throughout the tool.

## Download & Installation

**Clone the repository**  
```bash
git clone https://github.com/blu3OceanWaves/CoreView.git
cd CoreView
```
**Install Python dependencies**  
```bash
sudo apt update  
sudo apt install python3-pip python3-venv -y  
pip3 install rich psutil requests
```
**Make the tool globally accessible (optional)**  
```bash
sudo cp simplinfo.py /usr/local/bin/CoreView  
sudo chmod +x /usr/local/bin/CoreView
```
Now you can run it from any directory using:  
```bash
CoreView
```
## Usage

Run the tool directly with Python:  
```bash
python3 CoreView.py
```
Or globally if installed:  
```bash
CoreView
```
Follow the menu to view system information, security insights, and hints. Some features may require **root privileges**.

## Requirements

- Python 3.8+  
- `rich`  
- `psutil`  
- `requests`
- `speedtest-cli`

## 📌 Changelog
- **Version 2.0 – 30.08.2025**
- **Version 2.1 - 30.08.2025**

## ✨ New 
### V. 2.0
- Added **network utilities**: Ping Analyzer, DNS Lookup, Traceroute, Speed Test, ARP Table.  
- Enhanced **menu panels**  
### V. 2.1
#### Fixed
- Option 17 (Network Speed Test) now checks for internet connectivity before running.  
  Previously, running it immediately after system boot without network caused a Python exception.  
  Now, a clear message "No internet connection available ❌" is displayed instead.

## Contact

For bugs, feedback, or questions, connect with me on LinkedIn:  

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Yassin-blue?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/yassin-el-wardioui-34016b332/)

