#!/usr/bin/bash

  #exchanges
rabbitmqadmin declare exchange name=announcements_exchange type=fanout durable=true
rabbitmqadmin declare exchange name=rules_exchange type=fanout durable=true
rabbitmqadmin declare exchange name=routing_exchange type=topic durable=true

  #queues 
rabbitmqadmin declare queue name=announcements_queue durable=true
rabbitmqadmin declare queue name=rules_queue durable=true

#read users from conf file and fill arrays
config_file="users.yaml"
users_array=()

USERS=$(rabbitmqadmin list users name -f tsv)

while IFS= read -r line || [[ -n "$line" ]]; do

  if [[ "$line" =~ ^[[:space:]]*name[[:space:]]*:[[:space:]]*(.*)$ ]]; then
    users_array+=("${BASH_REMATCH[1]}")
  fi

done < "$config_file"

#for each user
for user in "${!users_array[@]}"; do  
    FOUND=0
    for USER in $USERS; do
      if [[ "$USER" == "${users_array[$user]}" ]]; then
              FOUND=1
        echo "User ${users_array[$user]} already exists"
      fi
    done
    #create rabbitmq user
  if [[ $FOUND -eq 0 ]]; then
    rabbitmqctl add_user "${users_array[$user]}" ""
  
    #remove PW (auth only through certificates)
  rabbitmqctl clear_password ${users_array[$user]}
  fi
    #private queue 
  rabbitmqadmin declare queue name=${users_array[$user]}
  rabbitmqadmin declare binding source="routing_exchange" destination="${users_array[$user]}" routing_key="#.""${users_array[$user]}"".#" destination_type="queue" 

    #writing permission on exchanges and reading permission on its own queue
  
  if [ ${users_array[$user]} = "broker_router" ]; then
    echo "setting broker_router permissions"
    rabbitmqctl set_user_tags broker_router administrator
    rabbitmqctl set_permissions -p / broker_router ".*" ".*" ".*"
  else
    echo "setting "${users_array[$user]}" permissions"
    rabbitmqctl set_permissions -p / ${users_array[$user]} "\$" "^(announcements_exchange|rules_exchange)\$" "^(${users_array[$user]})\$"
  fi

  rabbitmqadmin declare binding source="announcements_exchange" destination="announcements_queue"
  rabbitmqadmin declare binding source="rules_exchange" destination="rules_queue"
    
    #certificates generation
  if [[ "$FOUND" -eq 0 ]]; then
    ./cert_gen.sh ${users_array[$user]}
  fi
done
