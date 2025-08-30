#!/usr/bin/env python3
import sys
import os
import socket
import getpass
import subprocess
import pwd
import statistics
import re


# ------------------ Dependency Check ------------------
missing = []
for module in ["rich", "psutil", "requests"]:
    try:
        __import__(module)
    except ImportError:
        missing.append(module)

if missing:
    print("\n[!] Missing dependencies:", ", ".join(missing))
    print(" Install using:")
    print(" sudo apt install python3-" + " python3-".join(missing))
    print(" Or in a virtual environment:")
    print(" python3 -m venv ~/env")
    print(" source ~/env/bin/activate")
    print(" pip install " + " ".join(missing))
    print()
    sys.exit(1)

import psutil
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.prompt import Prompt

console = Console()

# ------------------ Helpers ------------------
def check_warn(condition: bool, message: str):
    if condition:
        console.print(f"[bold red][!] Security hint:[/bold red] {message}")

def panel_print(title, content, border="bright_blue"):
    console.print(Align.center(Panel(content, title=f"[bold yellow]{title}[/bold yellow]", border_style=border, width=80)))

def wait_for_enter():
    input("\nPress Enter to return to menu...")

# ------------------ Functions ------------------
def get_internal_ip():
    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
    except:
        ip = "Not available"
    panel_print("Internal IP & Hostname",
                f"[bold green]Hostname:[/bold green] {hostname}\n[bold cyan]Internal IP:[/bold cyan] {ip}")
    check_warn(ip.startswith("127."), "Internal IP is localhost; network may be inactive")
    wait_for_enter()

def get_external_ip():
    try:
        ip = requests.get("https://api.ipify.org").text
    except:
        ip = "Not available"
    panel_print("External IP", f"[bold magenta]External IP:[/bold magenta] {ip}")
    wait_for_enter()

def get_system_info():
    import platform
    sys_info = {
        "OS": platform.system(),
        "Kernel": platform.release(),
        "Version": platform.version(),
        "Architecture": platform.machine()
    }
    table = Table(title="System Info", show_header=True)
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    for k, v in sys_info.items():
        table.add_row(k, v)
    panel_print("System Info", Align.center(table))
    wait_for_enter()

def get_logged_in_users():
    users = [u.name for u in psutil.users()]
    panel_print("Logged-in Users", "\n".join(users))
    check_warn(len(users) > 3, "Multiple active users may indicate shared access")
    wait_for_enter()

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
    panel_print("All Users", Align.center(table))
    wait_for_enter()

def get_current_user():
    user = getpass.getuser()
    panel_print("Current User", f"[bold green]{user}[/bold green]")
    wait_for_enter()

def get_processes():
    table = Table(title="Top 5 Processes by CPU Usage")
    table.add_column("PID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("CPU%", style="magenta")
    for p in sorted(psutil.process_iter(['pid','name','cpu_percent']), key=lambda x: x.info['cpu_percent'], reverse=True)[:5]:
        table.add_row(str(p.info['pid']), p.info['name'], str(p.info['cpu_percent']))
    panel_print("Top Processes", Align.center(table))
    wait_for_enter()

def get_open_ports():
    try:
        result = subprocess.check_output("ss -tuln", shell=True, text=True)
        panel_print("Open Ports", result)
        check_warn("0.0.0.0" in result or "::" in result, "Open ports are accessible from any network; ensure firewall rules or port restrictions are applied")
    except Exception as e:
        panel_print("Open Ports", f"Error: {e}", border="red")
    wait_for_enter()

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
    wait_for_enter()

def check_firewall():
    try:
        result = subprocess.check_output("sudo ufw status", shell=True, text=True)
        panel_print("Firewall Status", result)
        check_warn("inactive" in result.lower(), "Firewall is inactive; consider enabling it or configuring iptables/nftables")
    except:
        panel_print("Firewall Status", "UFW not installed or sudo required", border="red")
    wait_for_enter()

def ssh_login_attempts():
    try:
        result = subprocess.check_output("journalctl _COMM=sshd -n 10 --no-pager", shell=True, text=True)
        panel_print("Recent SSH Login Attempts", result)
        check_warn("Failed password" in result, "Failed SSH logins detected; consider restricting root login or using fail2ban")
    except:
        panel_print("Recent SSH Login Attempts", "Cannot check logs: sudo may be required", border="red")
    wait_for_enter()

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
    wait_for_enter()

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
    wait_for_enter()

# ------------------ Utilities ------------------
def ping_analyzer():
    host = Prompt.ask("[bold blue]Enter host to ping[/bold blue]", console=console)
    if not host:
        console.print("[red]No host provided[/red]", justify="center")
        return
    count = Prompt.ask("[bold blue]How many packets?[/bold blue]", default="10", console=console)
    count = int(count) if count.isdigit() else 10

    try:
        result = subprocess.run(["ping", "-c", str(count), host], capture_output=True, text=True)
        output = result.stdout
    except Exception as e:
        panel_print("Ping Analyzer", f"Error: {e}", border="red")
        return

    times = [float(m.group(1)) for m in re.finditer(r"time=(\d+\.\d+)", output)]
    if not times:
        panel_print("Ping Analyzer", "No replies received ❌", border="red")
        return

    stats = {
        "min": min(times),
        "max": max(times),
        "avg": statistics.mean(times),
        "median": statistics.median(times),
        "loss": 100 - (len(times) / count * 100)
    }

    stats_text = "\n".join(f"{k:<6}: {v:.2f} ms" if k != "loss" else f"{k:<6}: {v:.1f}%" for k, v in stats.items())

    max_bar_width = 30
    max_time = max(times)
    bar_lines = []
    for t in times:
        bar_len = int((t / max_time) * max_bar_width)
        bar_color = "green" if t < 30 else "yellow" if t < 70 else "red"
        bar = f"[{bar_color}]" + "▉" * bar_len + "[/]"
        bar_lines.append(f"{bar} {t:.2f} ms")

    bars_text = "\n".join(bar_lines)
    connector_line = "─" * 60

    full_content = f"{stats_text}\n\n{connector_line}\n{bars_text}"
    panel_print("Ping Analyzer", full_content)
    wait_for_enter()

def dns_lookup():
    host = Prompt.ask("[bold blue]Enter hostname or IP[/bold blue]", console=console)
    if not host:
        console.print("[red]No host provided[/red]", justify="center")
        return
    try:
        ip = socket.gethostbyname(host)
        panel_print("DNS Lookup", f"[bold green]Hostname:[/bold green] {host}\n[bold cyan]IP:[/bold cyan] {ip}")
    except Exception as e:
        panel_print("DNS Lookup", f"Error: {e}", border="red")
    wait_for_enter()

def traceroute():
    host = Prompt.ask("[bold blue]Enter host for traceroute[/bold blue]", console=console)
    if not host:
        console.print("[red]No host provided[/red]", justify="center")
        return
    try:
        result = subprocess.check_output(f"traceroute {host} -m 15", shell=True, text=True)
        panel_print("Traceroute", result)
    except Exception as e:
        panel_print("Traceroute", f"Error: {e}", border="red")
    wait_for_enter()

def speed_test():
    try:
        import speedtest
    except ImportError:
        console.print("[red]speedtest module not installed. Run 'pip install speedtest-cli'[/red]")
        wait_for_enter()
        return
    st = speedtest.Speedtest()
    console.print("[yellow]Finding best server...[/yellow]", justify="center")
    st.get_best_server()
    down = st.download() / 1e6
    up = st.upload() / 1e6
    ping = st.results.ping
    panel_print("Network Speed Test", f"[bold green]Download:[/bold green] {down:.2f} Mbps\n"
                                         f"[bold green]Upload:[/bold green] {up:.2f} Mbps\n"
                                         f"[bold cyan]Ping:[/bold cyan] {ping} ms")
    wait_for_enter()

def arp_table():
    try:
        result = subprocess.check_output("arp -a", shell=True, text=True)
        if result.strip():
            panel_print("ARP Table", result)
        else:
            panel_print("ARP Table", "No entries found")
    except Exception as e:
        panel_print("ARP Table", f"Error: {e}", border="red")
    wait_for_enter()

# ------------------ Menu ------------------
def menu():
    while True:
        console.clear()
        # Banner
        banner = r"""
┏━┛┏━┃┏━┃┏━┛┃ ┃┛┏━┛┃┃┃
┃  ┃ ┃┏┏┛┏━┛┃ ┃┃┏━┛┃┃┃
━━┛━━┛┛ ┛━━┛ ┛ ┛━━┛━━┛
"""
        console.print(Align.center(banner, vertical="top"), style="bold cyan")

        net_panel = Panel(
            Align.center("[1] Internal IP & Hostname\n[2] External IP"),
            title="[bold cyan]Network Info[/bold cyan]",
            border_style="cyan",
            width=50
        )
        sys_panel = Panel(
            Align.center("[3] System Info\n[4] Logged-in Users\n[5] All Users\n[6] Current User\n[7] Top Processes"),
            title="[bold magenta]System Info[/bold magenta]",
            border_style="magenta",
            width=50
        )
        sec_panel = Panel(
            Align.center("[8] Open Ports\n[9] SUID/SGID Files\n[10] Firewall Status\n[11] Recent SSH Login Attempts\n[12] World-Writable Directories\n[13] Cron Jobs"),
            title="[bold green]Security Checks[/bold green]",
            border_style="green",
            width=50
        )
        util_panel = Panel(
            Align.center("[14] Ping Analyzer\n[15] DNS Lookup\n[16] Traceroute\n[17] Network Speed Test\n[18] ARP Table"),
            title="[bold blue]Utilities[/bold blue]",
            border_style="blue",
            width=50
        )

        console.print(Align.center(net_panel))
        console.print(Align.center(sys_panel))
        console.print(Align.center(sec_panel))
        console.print(Align.center(util_panel))

        exit_panel = Panel(
            Align.center("[0] Exit Tool"),
            title="[bold red]Exit[/bold red]",
            border_style="red",
            width=50
        )
        console.print("\n")
        console.print(Align.center(exit_panel))
        console.print("\n")

        choice = Prompt.ask("[bold yellow]Choose an option[/bold yellow]", console=console, show_default=False, default="---")

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
        elif choice == "14": ping_analyzer()
        elif choice == "15": dns_lookup()
        elif choice == "16": traceroute()
        elif choice == "17": speed_test()
        elif choice == "18": arp_table()
        elif choice == "0":
            console.print(Align.center("[bold red]Exiting Tool[/bold red]"))
            break
        else:
            console.print(Align.center("[bold red]Invalid choice[/bold red]"))
            wait_for_enter()

# ------------------ Main ------------------
if __name__ == "__main__":
    menu()
