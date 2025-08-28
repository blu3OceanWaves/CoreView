#!/usr/bin/env python3
import sys
import os
import socket
import getpass
import subprocess
import pwd

# ------------------ Dependency Check ------------------
missing = []
for module in ["rich", "psutil", "requests"]:
    try:
        __import__(module)
    except ImportError:
        missing.append(module)

if missing:
    print("\n[!] Missing dependencies:", ", ".join(missing))
    print("    Install using:")
    print("      sudo apt install python3-" + " python3-".join(missing))
    print("    Or in a virtual environment:")
    print("      python3 -m venv ~/env")
    print("      source ~/env/bin/activate")
    print("      pip install " + " ".join(missing))
    print()

import psutil
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# ------------------ Helpers ------------------
def check_warn(condition: bool, message: str):
    if condition:
        console.print(f"[bold red][!] Security hint:[/bold red] {message}")

def panel_print(title, content, border="bright_blue"):
    console.print(Panel(content, title=f"[bold yellow]{title}[/bold yellow]", border_style=border))

# ------------------ Functions ------------------

def get_internal_ip():
    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
    except:
        ip = "Not available"
    panel_print("Internal IP & Hostname", f"[bold green]Hostname:[/bold green] {hostname}\n[bold cyan]Internal IP:[/bold cyan] {ip}")
    check_warn(ip.startswith("127."), "Internal IP is localhost; network may be inactive")

def get_external_ip():
    try:
        ip = requests.get("https://api.ipify.org").text
    except:
        ip = "Not available"
    panel_print("External IP", f"[bold magenta]External IP:[/bold magenta] {ip}")

def get_system_info():
    import platform
    sys_info = {
        "System": platform.system(),
        "Release": platform.release(),
        "Version": platform.version(),
        "Architecture": platform.machine()
    }
    content = "\n".join([f"[bold cyan]{k}:[/bold cyan] {v}" for k,v in sys_info.items()])
    panel_print("System Info", content)

def get_logged_in_users():
    users = [u.name for u in psutil.users()]
    panel_print("Logged-in Users", "\n".join(users))
    check_warn(len(users) > 3, "Multiple active users may indicate shared access")

def list_all_users():
    table = Table(title="All System Users")
    table.add_column("Name", style="green")
    table.add_column("UID", style="cyan")
    table.add_column("Home", style="magenta")
    table.add_column("Shell", style="yellow")
    for p in pwd.getpwall():
        table.add_row(p.pw_name, str(p.pw_uid), p.pw_dir, p.pw_shell)
        if p.pw_uid == 0 and p.pw_name != "root":
            check_warn(True, f"User {p.pw_name} has root privileges, check!")
    console.print(table)

def get_current_user():
    user = getpass.getuser()
    panel_print("Current User", f"[bold green]{user}[/bold green]")

def get_processes():
    table = Table(title="Top 5 Processes by CPU Usage")
    table.add_column("PID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("CPU%", style="magenta")
    for p in sorted(psutil.process_iter(['pid','name','cpu_percent']), key=lambda x: x.info['cpu_percent'], reverse=True)[:5]:
        table.add_row(str(p.info['pid']), p.info['name'], str(p.info['cpu_percent']))
    console.print(table)

def get_open_ports():
    try:
        result = subprocess.check_output("ss -tuln", shell=True, text=True)
        panel_print("Open Ports", result)
        check_warn("0.0.0.0" in result or "::" in result, "Open ports are accessible from any network; ensure firewall rules or port restrictions are applied")
    except Exception as e:
        panel_print("Open Ports", f"Error: {e}", border="red")

def find_suid_files():
    try:
        result = subprocess.check_output("find / -perm /6000 -type f 2>/dev/null | head -n 20", shell=True, text=True)
        if result.strip():
            panel_print("SUID/SGID Files", result)
            check_warn(True, "SUID/SGID files found – verify necessity")
        else:
            panel_print("SUID/SGID Files", "None found")
    except Exception as e:
        panel_print("SUID/SGID Files", f"Error: {e}", border="red")

def check_firewall():
    try:
        result = subprocess.check_output("sudo ufw status", shell=True, text=True)
        panel_print("Firewall Status", result)
        check_warn("inactive" in result.lower(), "Firewall is inactive; consider enabling it or configuring iptables/nftables")
    except:
        panel_print("Firewall Status", "UFW not installed or sudo required", border="red")

def ssh_login_attempts():
    try:
        result = subprocess.check_output("journalctl _COMM=sshd -n 10 --no-pager", shell=True, text=True)
        panel_print("Recent SSH Login Attempts", result)
        check_warn("Failed password" in result, "Failed SSH logins detected; consider restricting root login or using fail2ban")
    except:
        panel_print("Recent SSH Login Attempts", "Cannot check logs: sudo may be required", border="red")

def check_world_writable():
    try:
        result = subprocess.check_output("find / -xdev -type d -perm -0002 -ls 2>/dev/null | head -n 20", shell=True, text=True)
        if result.strip():
            panel_print("World-Writable Directories", result)
            check_warn(True, "World-writable directories found – verify necessity")
        else:
            panel_print("World-Writable Directories", "None found")
    except:
        panel_print("World-Writable Directories", "Cannot check directories: sudo may be required", border="red")

def check_cron_jobs():
    try:
        result = subprocess.check_output("ls -al /etc/cron* /var/spool/cron/crontabs 2>/dev/null", shell=True, text=True)
        if result.strip():
            panel_print("Cron Jobs", result)
            check_warn(True, "Cron jobs exist – review for unauthorized entries")
        else:
            panel_print("Cron Jobs", "None found")
    except:
        panel_print("Cron Jobs", "Cannot check cron jobs: sudo may be required", border="red")

def check_kernel_version():
    try:
        version = subprocess.check_output("uname -r", shell=True, text=True).strip()
        panel_print("Kernel Version", version)
        check_warn("generic" in version.lower(), "Using generic kernel – ensure updates applied")
    except:
        panel_print("Kernel Version", "Could not retrieve kernel version", border="red")

# ------------------ Menu ------------------

def menu():
    while True:
        console.print(Panel(
            "[bold cyan]1.[/bold cyan] Internal IP & Hostname\n"
            "[bold cyan]2.[/bold cyan] External IP\n"
            "[bold cyan]3.[/bold cyan] System Info\n"
            "[bold cyan]4.[/bold cyan] Logged-in Users\n"
            "[bold cyan]5.[/bold cyan] All Users\n"
            "[bold cyan]6.[/bold cyan] Current User\n"
            "[bold cyan]7.[/bold cyan] Top Processes\n"
            "[bold cyan]8.[/bold cyan] Open Ports\n"
            "[bold cyan]9.[/bold cyan] SUID/SGID Files\n"
            "[bold cyan]10.[/bold cyan] Firewall Status\n"
            "[bold cyan]11.[/bold cyan] Recent SSH Login Attempts\n"
            "[bold cyan]12.[/bold cyan] World-Writable Directories\n"
            "[bold cyan]13.[/bold cyan] Cron Jobs\n"
            "[bold cyan]14.[/bold cyan] Kernel Version\n"
            "[bold cyan]15.[/bold cyan] Exit",
            title="[bold yellow]System Info Tool[/bold yellow]",
            border_style="bright_blue"
        ))

        choice = input("Choose an option: ").strip()

        if choice == "1": get_internal_ip()
        elif choice == "2": get_external_ip()
        elif choice == "3": get_system_info()
        elif choice == "4": get_logged_in_users()
        elif choice == "5": list_all_users()
        elif choice == "6": get_current_user()
        elif choice == "7": get_processes()
        elif choice == "8": get_open_ports()
        elif choice == "9": find_suid_files()
        elif choice == "10": check_firewall()
        elif choice == "11": ssh_login_attempts()
        elif choice == "12": check_world_writable()
        elif choice == "13": check_cron_jobs()
        elif choice == "14": check_kernel_version()
        elif choice == "15":
            console.print("[bold green]Exiting[/bold green]")
            break
        else:
            console.print("[bold red]Invalid choice[/bold red]\n")

# ------------------ Main ------------------

if __name__ == "__main__":
    menu()
