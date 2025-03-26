#!/bin/bash

# Delete users
echo "Retrieving users..."
USERS=$(rabbitmqadmin list users name -f tsv)

for USER in $USERS; do
  if [ "$USER" != "guest" ]; then
    echo "Deleting user: $USER"
    rabbitmqadmin delete user name="$USER"
  else
    echo "skipping guest"
  fi
done

# Delete queues
echo "Retrieving queues..."
QUEUES=$(rabbitmqadmin list queues name -f tsv)

for QUEUE in $QUEUES; do
    echo "Deleting queue: $QUEUE"
    rabbitmqadmin delete queue name="$QUEUE"
done

# Delete exchange except default (amq.*)
echo "Retrieving exchanges..."
EXCHANGES=$(rabbitmqadmin list exchanges name -f tsv | grep -vE '^amq\.')

for EXCHANGE in $EXCHANGES; do
    echo "Deleting exchange: $EXCHANGE"
    rabbitmqadmin delete exchange name="$EXCHANGE"
done

echo "RabbitMQ erased"
