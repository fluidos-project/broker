#!/bin/bash

# Check there is 1 param
if [ -z "$1" ]; then
    echo "Need 1 param"
    exit 1
fi

USR_NAME="$1"

# List binding
BINDINGS=$(rabbitmqadmin list bindings source destination routing_key -f tsv)

# For each binding delete if contains USR_NAME 
while IFS=$'\t' read -r SOURCE DESTINATION ROUTING_KEY; do
    # check if USR_NAME is contained in a destination or routing key
    # if [[ "$ROUTING_KEY" == *"$USR_NAME"* ]]; then
    if [[ "$ROUTING_KEY" == "#" ]]; then
        echo "Remove binding: Exchange '$SOURCE' → Queue '$DESTINATION' with Routing Key '$ROUTING_KEY'..."
        rabbitmqadmin delete binding source="$SOURCE" destination="$DESTINATION" destination_type="exchange" properties_key="$ROUTING_KEY"
    fi
    if [[ "$DESTINATION" == *"$USR_NAME"* ]]; then
    echo "Remove binding: Exchange '$SOURCE' → Queue '$DESTINATION' with Routing Key '$ROUTING_KEY'..."
        rabbitmqadmin delete binding source="$SOURCE" destination="$DESTINATION" destination_type="queue"
    fi

done <<< "$BINDINGS"

echo "Deletion complete"
