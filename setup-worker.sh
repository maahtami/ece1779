#!/bin/bash

# This script installs Docker and prepares the Droplet to join a Docker Swarm as a worker node.

# --- 1. SYSTEM UPDATE AND PREPARATION ---
echo "--- 1. Updating the system and installing prerequisites ---"
# Update all installed packages
sudo apt-get update -y
# Upgrade packages to their latest version
sudo apt-get upgrade -y
# Install necessary dependencies for Docker installation
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

# --- 2. INSTALL DOCKER ENGINE ---
echo "--- 2. Installing Docker Engine (CE) ---"
# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up the stable repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# --- 3. SWARM PREPARATION (Manual Join Required) ---
echo "--- 3. Docker Service Configured. Manual Join Required. ---"

# Start the Docker service
sudo systemctl start docker
# Enable Docker to start on boot
sudo systemctl enable docker

# --- 4. DISPLAY RESULTS ---
echo -e "\n======================================================="
echo "✅ WORKER NODE SETUP (DOCKER INSTALLED) COMPLETE"
echo "======================================================="
echo "The Docker Engine is installed and running."
echo -e "\nNEXT STEP: MANUALLY JOIN THE SWARM"
echo "1. SSH into your Manager Droplet (ims-swarm-manager)."
echo "2. Run 'sudo docker swarm join-token worker' to retrieve the join command."
echo "3. Execute that full command here on ims-swarm-worker-1."
echo ""
echo "Verification on Manager: Run 'sudo docker node ls' on the Manager Droplet to confirm status is 'Ready'."
echo "======================================================="