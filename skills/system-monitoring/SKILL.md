---
name: system-monitoring
description: System resource monitoring and management including CPU usage, memory status, disk space alerts, network statistics, process management, and automated health checks. Use when tasks involve checking system resources, monitoring performance, managing processes, alerting on resource limits, or diagnosing system issues.
---

# System Monitoring

Monitor system resources, manage processes, and perform health checks.

## Quick Start

```python
from scripts.system_monitor import SystemMonitor

mon = SystemMonitor()

# Quick health check
health = mon.health_check()
print(health['status'])  # 'healthy' or 'warning'
for alert in health['alerts']:
    print(f"Alert: {alert}")

# CPU usage
cpu = mon.get_cpu_info()
print(f"CPU: {cpu['percent']}%")

# Memory usage
mem = mon.get_memory_info()
print(f"Memory: {mem['virtual']['percent']}%")
```

## Setup

```bash
pip install psutil
```

## CPU Monitoring

```python
# Get CPU information
cpu = mon.get_cpu_info()

print(f"Overall usage: {cpu['percent']}%")
print(f"Per-core usage: {cpu['percent_per_cpu']}")
print(f"Physical cores: {cpu['count_physical']}")
print(f"Logical cores: {cpu['count_logical']}")

# Check if CPU is high
if mon.is_cpu_high(threshold=80):
    print("Warning: High CPU usage!")
```

## Memory Monitoring

```python
# Get memory information
mem = mon.get_memory_info()

# Virtual memory
print(f"Total RAM: {mem['virtual']['total_gb']} GB")
print(f"Available: {mem['virtual']['available_gb']} GB")
print(f"Used: {mem['virtual']['used_gb']} GB ({mem['virtual']['percent']}%)")

# Swap memory
print(f"Swap total: {mem['swap']['total_gb']} GB")
print(f"Swap used: {mem['swap']['used_gb']} GB ({mem['swap']['percent']}%)")

# Check if memory is high
if mon.is_memory_high(threshold=80):
    print("Warning: High memory usage!")
```

## Disk Monitoring

```python
# Check specific path
disk = mon.get_disk_usage('/')
print(f"Disk: {disk['used_gb']}/{disk['total_gb']} GB ({disk['percent']}%)")

# Check all disks
for disk in mon.get_all_disks():
    print(f"{disk['path']}: {disk['percent']}% full ({disk['free_gb']} GB free)")

# Check if disk is nearly full
if mon.is_disk_full(path='/', threshold=90):
    print("Warning: Disk nearly full!")

# Disk I/O statistics
io = mon.get_disk_io()
if io:
    print(f"Read: {io['read_mb']} MB")
    print(f"Written: {io['write_mb']} MB")
```

## Network Monitoring

```python
# Network I/O statistics
net = mon.get_network_info()

print(f"Sent: {net['gb_sent']} GB")
print(f"Received: {net['gb_recv']} GB")
print(f"Packets sent: {net['packets_sent']}")
print(f"Packets received: {net['packets_recv']}")

# Active network connections
connections = mon.get_network_connections(kind='tcp')
print(f"Active TCP connections: {len(connections)}")

for conn in connections[:5]:
    print(f"  {conn['local_addr']} -> {conn['remote_addr']} ({conn['status']})")
```

## Process Management

```python
# List top processes by memory
processes = mon.list_processes(sort_by='memory', top_n=10)

for proc in processes:
    print(f"{proc['name']} (PID {proc['pid']}): {proc['memory_mb']} MB")

# List top processes by CPU
processes = mon.list_processes(sort_by='cpu', top_n=10)

for proc in processes:
    print(f"{proc['name']} (PID {proc['pid']}): {proc['cpu_percent']}%")

# Get detailed process info
proc_info = mon.get_process_info(1234)
print(f"Name: {proc_info['name']}")
print(f"CPU: {proc_info['cpu_percent']}%")
print(f"Memory: {proc_info['memory_mb']} MB")
print(f"Status: {proc_info['status']}")

# Find process by name
matches = mon.find_process('python')
for proc in matches:
    print(f"Found: {proc['name']} (PID {proc['pid']})")

# Kill process (terminate gracefully)
mon.kill_process(1234, force=False)

# Force kill process
mon.kill_process(1234, force=True)
```

## System Information

```python
# General system info
info = mon.get_system_info()

print(f"OS: {info['platform']} {info['platform_release']}")
print(f"Hostname: {info['hostname']}")
print(f"Processor: {info['processor']}")
print(f"Architecture: {info['architecture']}")
print(f"Boot time: {info['boot_time']}")
print(f"Uptime: {info['uptime']}")

# Battery info (laptops)
battery = mon.get_battery_info()
if battery:
    print(f"Battery: {battery['percent']}%")
    print(f"Plugged in: {battery['plugged_in']}")
    print(f"Time left: {battery['time_left']}")

# Temperature (if available)
temps = mon.get_temperature()
if temps:
    print(f"Temperatures: {temps}")
```

## Health Checks

```python
# Perform health check
health = mon.health_check(
    cpu_threshold=80,
    memory_threshold=80,
    disk_threshold=90
)

print(f"Status: {health['status']}")  # 'healthy' or 'warning'

if health['alerts']:
    print("Alerts:")
    for alert in health['alerts']:
        print(f"  - {alert}")

# Summary
print(f"CPU: {health['summary']['cpu_percent']}%")
print(f"Memory: {health['summary']['memory_percent']}%")
for disk in health['summary']['disk_usage']:
    print(f"Disk {disk['path']}: {disk['percent']}%")
```

## Comprehensive Report

```python
# Generate full system report
report = mon.generate_report()

# Report includes:
# - System information
# - CPU usage
# - Memory usage
# - Disk usage (all disks)
# - Network statistics
# - Top 10 processes
# - Health check results
# - Battery status (if available)

# Save to JSON
import json
with open('system_report.json', 'w') as f:
    json.dump(report, f, indent=2)
```

## Common Workflows

### Monitor and Alert

```python
import time

while True:
    health = mon.health_check(
        cpu_threshold=80,
        memory_threshold=85,
        disk_threshold=90
    )

    if health['alerts']:
        print(f"[{health['timestamp']}] ALERTS:")
        for alert in health['alerts']:
            print(f"  {alert}")
            # Send notification, email, etc.

    time.sleep(60)  # Check every minute
```

### Find Memory Hogs

```python
# Find processes using most memory
processes = mon.list_processes(sort_by='memory', top_n=20)

print("Top memory consumers:")
for proc in processes:
    if proc['memory_mb'] > 500:  # Over 500 MB
        print(f"  {proc['name']} (PID {proc['pid']}): {proc['memory_mb']} MB")
```

### Disk Space Alert

```python
# Check all disks and alert if any are nearly full
for disk in mon.get_all_disks():
    if disk['percent'] > 85:
        print(f"WARNING: Disk {disk['path']} is {disk['percent']}% full!")
        print(f"  {disk['free_gb']} GB remaining")
```

### Kill Unresponsive Process

```python
# Find and kill unresponsive process
matches = mon.find_process('hung_app')

if matches:
    for proc in matches:
        print(f"Killing {proc['name']} (PID {proc['pid']})")
        try:
            mon.kill_process(proc['pid'], force=True)
            print("Killed successfully")
        except Exception as e:
            print(f"Failed: {e}")
```

### System Performance Log

```python
import json
from datetime import datetime

# Log system stats every hour
def log_performance():
    report = mon.generate_report()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"system_log_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Logged to {filename}")

# Run periodically
import time
while True:
    log_performance()
    time.sleep(3600)  # Every hour
```

### Resource Usage Dashboard

```python
def print_dashboard():
    cpu = mon.get_cpu_info()
    mem = mon.get_memory_info()
    disks = mon.get_all_disks()
    net = mon.get_network_info()

    print("=" * 50)
    print("SYSTEM DASHBOARD")
    print("=" * 50)
    print(f"CPU Usage: {cpu['percent']}%")
    print(f"Memory: {mem['virtual']['used_gb']}/{mem['virtual']['total_gb']} GB ({mem['virtual']['percent']}%)")

    print("\nDisks:")
    for disk in disks:
        print(f"  {disk['path']}: {disk['used_gb']}/{disk['total_gb']} GB ({disk['percent']}%)")

    print(f"\nNetwork:")
    print(f"  Sent: {net['gb_sent']} GB")
    print(f"  Received: {net['gb_recv']} GB")

    print("\nTop Processes (Memory):")
    for proc in mon.list_processes(sort_by='memory', top_n=5):
        print(f"  {proc['name']}: {proc['memory_mb']} MB")

    print("=" * 50)

# Refresh every 5 seconds
import time
while True:
    print_dashboard()
    time.sleep(5)
```

## Platform Differences

### Windows

- Full process management
- `num_handles` available
- Battery info on laptops
- Network connections may require admin

### Linux

- Full functionality
- `sensors` package for temperature monitoring
- Load average available
- May need `sudo` for some process operations

### macOS

- Full functionality
- Battery info on laptops
- Some features may need permissions

## Thresholds

Recommended alert thresholds:

- **CPU**: 80% (sustained high usage)
- **Memory**: 85% (before swap heavy use)
- **Disk**: 90% (time to free space)
- **Swap**: 50% (memory pressure indicator)

Adjust based on:

- System type (server vs desktop)
- Normal workload
- Available resources
- Application requirements

## Performance Impact

- Lightweight: Most calls are fast (<10ms)
- CPU percent requires ~1 second for accuracy
- Process iteration scales with process count
- Network connections may be slow with many connections

## Tips & Best Practices

1. **Use health_check() for regular monitoring** - includes all key metrics
2. **Cache results** when checking multiple metrics at once
3. **Set appropriate thresholds** for your system/workload
4. **Monitor trends** not just current values
5. **Log to file** for historical analysis
6. **Combine with alerts** (email, notifications) for automation
7. **Use process name search** instead of hardcoded PIDs
8. **Be careful with kill_process()** - verify before killing

## Dependencies

```bash
pip install psutil
```

## Limitations

- Temperature monitoring platform-dependent
- Some metrics require admin/root privileges
- Battery info only on laptops
- Load average not available on Windows
- Network connections listing can be slow with many connections
