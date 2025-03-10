#!/bin/bash

METRICS_FILE="metrics.yaml"

update_latency() {
    local client=$1
    local ip=$2

    if [[ -z "$ip" || "$ip" == "null" ]]; then
        echo "IP not valid for $client, skipping"
        return
    fi

    # Pick the latency from the ping command
    latency=$(ping -c 4 "$ip" | awk -F'/' '/rtt/ {print $5}')

    if [[ -n "$latency" ]]; then
        echo "Updating latency for $client ($ip) to $latency ms"

        # yq to modify YAML
        yq eval "(.[] | select(.${client}).${client}.latency) |= $latency" -i "$METRICS_FILE"
    else
        echo "Error pinging $client ($ip)"
    fi
}

while true; do
    # Get list client IP
    clients=$(yq eval '.[] | keys | .[]' "$METRICS_FILE")

    for client in $clients; do
        ip=$(yq eval ".[] | select(.${client}).${client}.ip" "$METRICS_FILE")
        update_latency "$client" "$ip"
    done

    echo "See you in 2 mins..."
    sleep 120
done
