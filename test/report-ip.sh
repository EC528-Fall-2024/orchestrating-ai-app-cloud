#!/bin/bash
# Get the control server's private IP
CONTROL_PRIV_IP=$(curl -s -X POST \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://get-private-ip-531274461726.us-central1.run.app | jq -r .private_ip)
# Get this instance's private IP
PRIVATE_IP=$(curl -H "Metadata-Flavor: Google" \
  http://169.254.169.254/computeMetadata/v1/instance/network-interfaces/0/ip)
USER_HOSTNAME=$(cat /etc/hostname)
# Construct the JSON payload
#PAYLOAD=$(jq -n --arg ip "$PRIVATE_IP" '{"ip":$ip}')
PAYLOAD=$(jq -n --arg ip "$PRIVATE_IP" --arg hostname "$USER_HOSTNAME" \
  '{"ip":$ip, "hostname":$hostname}')
# Send the request to the control server
curl -X POST "http://$CONTROL_PRIV_IP:5000/provision" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD"