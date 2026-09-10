#!/bin/bash
sudo cp configs/logind.conf /etc/systemd/logind.conf.d/override.conf 2>/dev/null || true
sudo systemctl restart systemd-logind
sudo systemctl enable --now tailscaled
