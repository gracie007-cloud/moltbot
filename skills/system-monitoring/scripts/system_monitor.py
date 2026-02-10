#!/usr/bin/env python3
"""
System monitoring: CPU, memory, disk, network, processes.
Requires: psutil
Install: pip install psutil
"""

import psutil
import platform
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class SystemMonitor:
    
    def __init__(self):
        """Initialize system monitor."""
        self.boot_time = datetime.fromtimestamp(psutil.boot_time())
    
    # ===== CPU Monitoring =====
    
    def get_cpu_info(self):
        """Get CPU information and usage."""
        return {
            'percent': psutil.cpu_percent(interval=1),
            'percent_per_cpu': psutil.cpu_percent(interval=1, percpu=True),
            'count_physical': psutil.cpu_count(logical=False),
            'count_logical': psutil.cpu_count(logical=True),
            'frequency': {
                'current': psutil.cpu_freq().current if psutil.cpu_freq() else None,
                'min': psutil.cpu_freq().min if psutil.cpu_freq() else None,
                'max': psutil.cpu_freq().max if psutil.cpu_freq() else None
            },
            'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
    
    def is_cpu_high(self, threshold=80):
        """Check if CPU usage is high."""
        usage = psutil.cpu_percent(interval=1)
        return usage > threshold
    
    # ===== Memory Monitoring =====
    
    def get_memory_info(self):
        """Get memory usage information."""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'virtual': {
                'total': mem.total,
                'available': mem.available,
                'used': mem.used,
                'free': mem.free,
                'percent': mem.percent,
                'total_gb': round(mem.total / 1024**3, 2),
                'available_gb': round(mem.available / 1024**3, 2),
                'used_gb': round(mem.used / 1024**3, 2)
            },
            'swap': {
                'total': swap.total,
                'used': swap.used,
                'free': swap.free,
                'percent': swap.percent,
                'total_gb': round(swap.total / 1024**3, 2),
                'used_gb': round(swap.used / 1024**3, 2)
            }
        }
    
    def is_memory_high(self, threshold=80):
        """Check if memory usage is high."""
        return psutil.virtual_memory().percent > threshold
    
    # ===== Disk Monitoring =====
    
    def get_disk_usage(self, path='/'):
        """Get disk usage for specific path."""
        usage = psutil.disk_usage(path)
        return {
            'path': path,
            'total': usage.total,
            'used': usage.used,
            'free': usage.free,
            'percent': usage.percent,
            'total_gb': round(usage.total / 1024**3, 2),
            'used_gb': round(usage.used / 1024**3, 2),
            'free_gb': round(usage.free / 1024**3, 2)
        }
    
    def get_all_disks(self):
        """Get usage for all mounted disks."""
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = self.get_disk_usage(partition.mountpoint)
                usage['device'] = partition.device
                usage['fstype'] = partition.fstype
                disks.append(usage)
            except (PermissionError, OSError):
                continue
        return disks
    
    def is_disk_full(self, path='/', threshold=90):
        """Check if disk is nearly full."""
        return psutil.disk_usage(path).percent > threshold
    
    def get_disk_io(self):
        """Get disk I/O statistics."""
        io = psutil.disk_io_counters()
        if io:
            return {
                'read_count': io.read_count,
                'write_count': io.write_count,
                'read_bytes': io.read_bytes,
                'write_bytes': io.write_bytes,
                'read_mb': round(io.read_bytes / 1024**2, 2),
                'write_mb': round(io.write_bytes / 1024**2, 2)
            }
        return None
    
    # ===== Network Monitoring =====
    
    def get_network_info(self):
        """Get network I/O statistics."""
        io = psutil.net_io_counters()
        return {
            'bytes_sent': io.bytes_sent,
            'bytes_recv': io.bytes_recv,
            'packets_sent': io.packets_sent,
            'packets_recv': io.packets_recv,
            'mb_sent': round(io.bytes_sent / 1024**2, 2),
            'mb_recv': round(io.bytes_recv / 1024**2, 2),
            'gb_sent': round(io.bytes_sent / 1024**3, 2),
            'gb_recv': round(io.bytes_recv / 1024**3, 2)
        }
    
    def get_network_connections(self, kind='inet'):
        """
        Get active network connections.
        
        Args:
            kind: 'inet', 'inet4', 'inet6', 'tcp', 'udp', 'all'
        """
        connections = []
        for conn in psutil.net_connections(kind=kind):
            connections.append({
                'fd': conn.fd,
                'family': str(conn.family),
                'type': str(conn.type),
                'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                'remote_addr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                'status': conn.status,
                'pid': conn.pid
            })
        return connections
    
    # ===== Process Management =====
    
    def list_processes(self, sort_by='memory', top_n=10):
        """
        List running processes.
        
        Args:
            sort_by: 'cpu', 'memory', 'name', 'pid'
            top_n: Number of processes to return
        """
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                pinfo['memory_mb'] = round(proc.memory_info().rss / 1024**2, 2)
                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort
        if sort_by == 'cpu':
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        elif sort_by == 'memory':
            processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
        elif sort_by == 'name':
            processes.sort(key=lambda x: x.get('name', ''))
        elif sort_by == 'pid':
            processes.sort(key=lambda x: x.get('pid', 0))
        
        return processes[:top_n]
    
    def get_process_info(self, pid):
        """Get detailed information about a process."""
        try:
            proc = psutil.Process(pid)
            
            return {
                'pid': proc.pid,
                'name': proc.name(),
                'exe': proc.exe(),
                'cwd': proc.cwd(),
                'cmdline': proc.cmdline(),
                'status': proc.status(),
                'username': proc.username(),
                'created': datetime.fromtimestamp(proc.create_time()).isoformat(),
                'cpu_percent': proc.cpu_percent(interval=0.1),
                'memory_percent': proc.memory_percent(),
                'memory_mb': round(proc.memory_info().rss / 1024**2, 2),
                'num_threads': proc.num_threads(),
                'num_handles': proc.num_handles() if hasattr(proc, 'num_handles') else None
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            raise Exception(f"Cannot access process {pid}: {e}")
    
    def find_process(self, name):
        """Find processes by name."""
        matches = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if name.lower() in proc.info['name'].lower():
                    matches.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return matches
    
    def kill_process(self, pid, force=False):
        """
        Kill a process.
        
        Args:
            pid: Process ID
            force: Use SIGKILL instead of SIGTERM (force=True)
        """
        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
            else:
                proc.terminate()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            raise Exception(f"Cannot kill process {pid}: {e}")
    
    # ===== System Information =====
    
    def get_system_info(self):
        """Get general system information."""
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'boot_time': self.boot_time.isoformat(),
            'uptime': str(datetime.now() - self.boot_time)
        }
    
    def get_battery_info(self):
        """Get battery information (if available)."""
        battery = psutil.sensors_battery()
        if battery:
            return {
                'percent': battery.percent,
                'plugged_in': battery.power_plugged,
                'time_left': str(timedelta(seconds=battery.secsleft)) if battery.secsleft != psutil.POWER_TIME_UNLIMITED else 'Unlimited'
            }
        return None
    
    def get_temperature(self):
        """Get CPU temperature (if available)."""
        if hasattr(psutil, 'sensors_temperatures'):
            temps = psutil.sensors_temperatures()
            if temps:
                return temps
        return None
    
    # ===== Health Checks =====
    
    def health_check(self, cpu_threshold=80, memory_threshold=80, disk_threshold=90):
        """
        Perform system health check.
        
        Returns:
            Dict with status and alerts
        """
        alerts = []
        
        # CPU
        cpu = self.get_cpu_info()
        if cpu['percent'] > cpu_threshold:
            alerts.append(f"High CPU usage: {cpu['percent']}%")
        
        # Memory
        mem = self.get_memory_info()
        if mem['virtual']['percent'] > memory_threshold:
            alerts.append(f"High memory usage: {mem['virtual']['percent']}%")
        
        # Disk
        for disk in self.get_all_disks():
            if disk['percent'] > disk_threshold:
                alerts.append(f"Disk {disk['path']} nearly full: {disk['percent']}%")
        
        status = 'healthy' if not alerts else 'warning'
        
        return {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'alerts': alerts,
            'summary': {
                'cpu_percent': cpu['percent'],
                'memory_percent': mem['virtual']['percent'],
                'disk_usage': [{'path': d['path'], 'percent': d['percent']} for d in self.get_all_disks()]
            }
        }
    
    # ===== Reporting =====
    
    def generate_report(self):
        """Generate comprehensive system report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'system': self.get_system_info(),
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disks': self.get_all_disks(),
            'network': self.get_network_info(),
            'top_processes': self.list_processes(top_n=10),
            'health': self.health_check(),
            'battery': self.get_battery_info()
        }


if __name__ == '__main__':
    import json
    
    monitor = SystemMonitor()
    
    # Generate and print report
    report = monitor.generate_report()
    print(json.dumps(report, indent=2))
    
    # Health check
    health = monitor.health_check()
    if health['alerts']:
        print("\nALERTS:")
        for alert in health['alerts']:
            print(f"  - {alert}")
