#!/bin/bash

# --- 1. CONFIGURATION ---
# Default network interface to check the IP (usually eth0 or ensX)
NETWORK_INTERFACE="eth0"

# CHANGED: Setting the default user to 'ubuntu'. 
# This is common on fresh DigitalOcean Ubuntu Droplets.
# If you run the script as 'root', the group assignment will skip safely, 
# and you can manually switch to a non-root user later if desired.
DOCKER_USER="ubuntu" 

# --- 2. SYSTEM UPDATE AND PREPARATION ---
echo "--- 1. Updating the system and installing prerequisites ---"
# Update all installed packages
sudo apt-get update -y
# Upgrade packages to their latest version
sudo apt-get upgrade -y
# Install necessary dependencies for Docker installation
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

# --- 3. INSTALL DOCKER ENGINE ---
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

# --- 4. POST-INSTALLATION SETUP ---
echo "--- 3. Configuring Docker permissions and starting service ---"
# Start the Docker service
sudo systemctl start docker
# Enable Docker to start on boot
sudo systemctl enable docker

# Add the specified user to the 'docker' group to run commands without sudo
# If you run this script as 'root', 'root' can already run docker commands.
if id -u "$DOCKER_USER" >/dev/null 2>&1; then
    sudo usermod -aG docker "$DOCKER_USER"
    echo "User '$DOCKER_USER' added to the 'docker' group. Log out and back in to apply."
else
    echo "Note: User '$DOCKER_USER' does not exist. Docker commands will require 'sudo' or be run as 'root'."
fi

# --- 5. SWARM INITIALIZATION ---
echo "--- 4. Initializing Docker Swarm Manager ---"

# Get the Public IP of the Droplet
PUBLIC_IP=$(curl -s checkip.amazonaws.com)

if [ -z "$PUBLIC_IP" ]; then
    echo "ERROR: Could not automatically determine public IP. Please check network settings."
    exit 1
fi

echo "Public IP detected: $PUBLIC_IP"

# Initialize the swarm using the public IP as the advertise address
# --listen-addr 0.0.0.0 is often the default, but explicitly setting the advertise-addr is critical
sudo docker swarm init --advertise-addr "$PUBLIC_IP"

# --- 6. DISPLAY RESULTS AND NEXT STEPS ---
echo -e "\n======================================================="
echo "✅ DOCKER SWARM MANAGER SETUP COMPLETE"
echo "======================================================="

echo "PUBLIC IP ADDRESS:"
echo "$PUBLIC_IP"

echo -e "\nSWARM STATUS:"
sudo docker info | grep "Swarm:"

echo -e "\nWORKER NODE JOIN COMMAND (Copy this command for your worker Droplets):"
# Extract the worker join token
JOIN_TOKEN=$(sudo docker swarm join-token worker -q)

echo "sudo docker swarm join --token $JOIN_TOKEN $PUBLIC_IP:2377"

echo -e "\n======================================================="
echo "NEXT STEPS:"
echo "1. Run the join command above on any new worker Droplets."
echo "2. From this manager node, run 'sudo docker node ls' to see all connected nodes."
echo "3. You can now deploy your stack: 'sudo docker stack deploy -c docker-stack.yml ims_stack'"
echo "4. IMPORTANT: If you added 'ubuntu' to the docker group, you must log out and log back in for the changes to take effect."
echo "======================================================="