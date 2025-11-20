"""
System health monitoring endpoint for managers.
Provides DigitalOcean droplet metrics and Docker service logs.
"""
import os
import subprocess
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from app.routers.dependencies import get_current_manager
from app.models.user import User
import requests

router = APIRouter(prefix="/health", tags=["health"])


class HealthMetrics:
    """Helper class to fetch DigitalOcean metrics and Docker logs"""
    
    def __init__(self):
        self.do_token = os.getenv("DIGITALOCEAN_TOKEN")
        self.do_droplet_ids = os.getenv("DIGITALOCEAN_DROPLET_IDS", "").split(",")
        self.do_api_url = "https://api.digitalocean.com/v2"
        # Adjusted service names to match the new docker-compose.yaml convention (stackname_service)
        self.docker_services = ["ims_stack_api", "ims_stack_db", "ims_stack_frontend"] 
    
    def get_droplet_metrics(self) -> List[Dict[str, Any]]:
        """
        Fetch metrics from DigitalOcean for configured droplets.
        Returns CPU, memory, and disk usage metrics.
        """
        if not self.do_token:
            return []
        
        droplets = []
        headers = {
            "Authorization": f"Bearer {self.do_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Fetch droplet info
            response = requests.get(
                f"{self.do_api_url}/droplets",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            all_droplets = response.json().get("droplets", [])
            
            # Filter by configured IDs or get first droplet
            droplet_ids = [d.strip() for d in self.do_droplet_ids if d.strip()]
            if droplet_ids:
                filtered_droplets = [d for d in all_droplets if str(d["id"]) in droplet_ids]
            else:
                filtered_droplets = all_droplets[:1]  # Default to first droplet
            
            for droplet in filtered_droplets:
                droplet_id = droplet["id"]
                # Fetch total resources for usage calculation
                total_memory_mb = droplet.get("memory", 0) # Memory in MB
                total_disk_gb = droplet.get("disk", 0)     # Disk in GB

                metrics = {
                    "droplet_id": droplet_id,
                    "name": droplet.get("name", "Unknown"),
                    "status": droplet.get("status", "unknown"),
                    "memory_mb": total_memory_mb,
                    "vcpus": droplet.get("vcpus", 0),
                    "disk_gb": total_disk_gb,
                    "cpu_usage": None,
                    "memory_usage": None,  # Will be calculated
                    "disk_usage": None,    # Will be calculated
                    # Disk I/O fields explicitly removed as per request
                    # "disk_read_bytes": None,
                    # "disk_write_bytes": None,
                }
                
                # Fetch monitoring metrics (CPU, Memory, Disk)
                metrics_data = self._fetch_monitoring_metrics(
                    droplet_id,
                    headers,
                    total_memory_mb, # Passed for memory usage calculation
                    total_disk_gb    # Passed for disk usage calculation
                )
                if metrics_data:
                    metrics.update(metrics_data)
                
                droplets.append(metrics)
            
            return droplets
            
        except Exception as e:
            print(f"Error fetching DigitalOcean metrics: {e}")
            return []
    
    def _fetch_monitoring_metrics(
        self,
        droplet_id: int,
        headers: Dict,
        total_memory_mb: int,
        total_disk_gb: int,
    ) -> Optional[Dict]:
        """
        Fetch CPU, memory, and disk usage metrics for a specific droplet.
        Disk I/O metrics have been removed.
        """
        metrics = {}
        
        # Define the time window (required by DO Monitoring API)
        current_timestamp = int(datetime.now().timestamp())
        end_time = current_timestamp - 10 # secs ago
        start_time = end_time - 80 # secs ago
        
        params = {
            "host_id": droplet_id, 
            "start": start_time,
            "end": end_time  
        }

        # --- 1. Fetch CPU metrics ---
        try:
            cpu_response = requests.get(
                f"{self.do_api_url}/monitoring/metrics/droplet/cpu",
                params=params,
                headers=headers,
                timeout=10
            )
            cpu_response.raise_for_status()
            cpu_data = cpu_response.json().get("data", {}).get("result", [])
            
            mode_deltas = {}
            
            # 1. Collect first and last values for all modes
            for series in cpu_data:
                mode = series.get("metric", {}).get("mode")
                values = series.get("values", [])
                
                if mode and values and len(values) >= 2:
                    # Values are [timestamp, value] pairs, get first and last value
                    first_val = float(values[0][1])
                    last_val = float(values[-1][1])
                    
                    # Calculate delta (change over time window)
                    delta = last_val - first_val
                    if delta >= 0:
                        mode_deltas[mode] = delta
            
            idle_delta = mode_deltas.get("idle", 0)
            
            # 2. Calculate Total CPU Delta (Sum of all mode deltas)
            total_delta = sum(mode_deltas.values())

            # 3. Calculate CPU Usage: 100 * (1 - (Idle_Delta / Total_Delta))
            if total_delta > 0:
                usage_rate = 1.0 - (idle_delta / total_delta)
                metrics["cpu_usage"] = round(usage_rate * 100.0, 2)
            else:
                metrics["cpu_usage"] = 0.0 # No activity detected

        except Exception as e:
            print(f"Error fetching CPU metrics for droplet {droplet_id}: {e}")
            metrics["cpu_usage"] = None


        # --- 2. Fetch Memory Usage metrics ---
        if total_memory_mb > 0:
            try:
                # CORRECTED ENDPOINT: Use 'memory_available' to find how much memory is free/available
                mem_response = requests.get(
                    f"{self.do_api_url}/monitoring/metrics/droplet/memory_available",
                    params={**params, "aggregate": "min"}, # Use 'min' for memory available
                    headers=headers,
                    timeout=10
                )
                mem_response.raise_for_status()
                mem_data = mem_response.json().get("data", {}).get("result", [])
                
                if mem_data and mem_data[0].get("values"):
                    # DO returns memory available in bytes. Use the latest value.
                    mem_available_bytes = float(mem_data[0]["values"][-1][1]) 
                    
                    # Convert total_memory_mb to bytes
                    total_memory_bytes = total_memory_mb * 1024 * 1024 
                    
                    if total_memory_bytes > 0:
                        # Calculate memory used in bytes: Total - Available
                        mem_used_bytes = total_memory_bytes - mem_available_bytes
                        
                        # Calculate usage percentage: (Used / Total) * 100
                        # Note: We cap usage at 100% just in case of slight reporting errors
                        usage_percent = max(0.0, (mem_used_bytes / total_memory_bytes) * 100.0)
                        metrics["memory_usage"] = round(usage_percent, 2)
                    else:
                        metrics["memory_usage"] = 0.0
                        
            except Exception as e:
                print(f"Error fetching Memory metrics for droplet {droplet_id}: {e}")
                metrics["memory_usage"] = None
        else:
            metrics["memory_usage"] = 0.0
        

        # --- 3. Fetch Disk Usage metrics (File system utilization using disk_gb) ---
        if total_disk_gb > 0:
            try:
                # 3a. Fetch free disk space from monitoring (for root mount point '/')
                free_response = requests.get(
                    f"{self.do_api_url}/monitoring/metrics/droplet/filesystem_free",
                    params={**params, "aggregate": "min"},
                    headers=headers,
                    timeout=10
                )
                free_response.raise_for_status()
                free_data = free_response.json().get("data", {}).get("result", [])
                
                # Find the free series for the root filesystem
                root_free_series = next(
                    (s for s in free_data if s.get("metric", {}).get("mountpoint") == "/"),
                    None
                )
                
                if root_free_series and root_free_series.get("values"):
                    
                    # Disk free is reported in bytes. Get the latest value.
                    disk_free_bytes = float(root_free_series["values"][-1][1])
                    
                    # Convert total_disk_gb (from Droplet metadata) to bytes
                    total_disk_bytes = total_disk_gb * 1024 * 1024 * 1024 

                    if total_disk_bytes > 0:
                        # Calculate used bytes: Total Bytes - Free Bytes
                        disk_used_bytes = total_disk_bytes - disk_free_bytes
                        
                        # Calculate used percentage: (Used Bytes / Total Bytes) * 100
                        # We use max(0.0, ...) in case the API reports slightly more free space than the metadata total.
                        usage_percent = max(0.0, (disk_used_bytes / total_disk_bytes)) * 100.0
                        metrics["disk_usage"] = round(usage_percent, 2)
                    else:
                        metrics["disk_usage"] = 0.0
                        
                else:
                    # If free data for root is not available, default to 0.0
                    metrics["disk_usage"] = 0.0
                        
            except Exception as e:
                print(f"Error fetching Disk metrics for droplet {droplet_id}: {e}")
                metrics["disk_usage"] = None
        else:
             metrics["disk_usage"] = 0.0

        return metrics
    
    def get_docker_logs(self, service_name: str, lines: int = 50) -> List[str]:
        """
        Get recent logs from a Docker service.
        Works when running inside Docker Swarm or as standalone containers.
        """
        try:
            # Try Docker service logs (Swarm mode)
            try:
                result = subprocess.run(
                    ["docker", "service", "logs", service_name, f"--tail={lines}"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return result.stdout.strip().split("\n")
            except Exception:
                pass
            
            # Fallback to container logs (Compose or standalone)
            result = subprocess.run(
                ["docker", "logs", service_name, f"--tail={lines}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip().split("\n")
            
            return [f"Could not retrieve logs for {service_name}"]
            
        except Exception as e:
            return [f"Error fetching logs: {str(e)}"]
    
    def get_all_service_logs(self, lines: int = 50) -> Dict[str, List[str]]:
        """Get logs from all configured Docker services"""
        logs = {}
        for service in self.docker_services:
            logs[service] = self.get_docker_logs(service, lines)
        return logs


@router.get("/system-metrics")
async def get_system_metrics(
    current_user: User = Depends(get_current_manager),
    lines: int = 50
) -> Dict[str, Any]:
    """
    Get system health metrics including:
    - DigitalOcean droplet CPU, memory, and disk usage
    - Docker service logs (last N lines)
    
    Only accessible by managers.
    """
    health = HealthMetrics()
    
    try:
        droplet_metrics = health.get_droplet_metrics()
        service_logs = health.get_all_service_logs(lines)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "droplets": droplet_metrics,
            "service_logs": service_logs,
            "services": health.docker_services,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching health metrics: {str(e)}")


@router.get("/service-logs/{service_name}")
async def get_service_logs(
    service_name: str,
    lines: int = 100,
    current_user: User = Depends(get_current_manager),
) -> Dict[str, Any]:
    """
    Get logs from a specific Docker service.
    
    Only accessible by managers.
    
    Parameters:
    - service_name: Docker service or container name
    - lines: Number of log lines to retrieve (default: 100)
    """
    health = HealthMetrics()
    
    # Security: only allow configured services
    if service_name not in health.docker_services:
        raise HTTPException(
            status_code=403,
            detail=f"Service {service_name} not in allowed list"
        )
    
    logs = health.get_docker_logs(service_name, lines)
    
    return {
        "service": service_name,
        "timestamp": datetime.utcnow().isoformat(),
        "log_lines": lines,
        "logs": logs,
    }


@router.get("/droplet-metrics")
async def get_droplet_metrics_endpoint(
    current_user: User = Depends(get_current_manager),
) -> Dict[str, Any]:
    """
    Get DigitalOcean droplet metrics (CPU, memory, disk usage).
    
    Only accessible by managers.
    """
    health = HealthMetrics()
    
    try:
        droplet_metrics = health.get_droplet_metrics()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "droplets": droplet_metrics,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching droplet metrics: {str(e)}")