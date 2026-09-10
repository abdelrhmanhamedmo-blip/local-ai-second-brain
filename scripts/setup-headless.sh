#!/bin/bash
<<<<<<< HEAD
sudo cp configs/logind.conf /etc/systemd/logind.conf.d/override.conf 2>/dev/null || true
sudo systemctl restart systemd-logind
sudo systemctl enable --now tailscaled
=======
# Enable headless operation on Fedora
echo "Configuring logind.conf..."
sudo cp configs/logind.conf /etc/systemd/logind.conf.d/override.conf 2>/dev/null || true
sudo systemctl restart systemd-logind

# Ensure Tailscale daemon is running
sudo systemctl enable --now tailscaled
echo "Setup complete!"
>>>>>>> 7819e14 (feat: add local AI content generation script via Ollama API)
