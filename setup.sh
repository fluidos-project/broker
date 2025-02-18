#!/usr/bin/bash
#EXTERNAL DEFAULT EXCHANGE
rabbitmqadmin declare exchange name=DefaultPeerRequest type=topic durable=true

#INTERNAL TIERS EXCHANGES
rabbitmqadmin declare exchange name=Tier1 type=fanout durable=true internal=true
rabbitmqadmin declare exchange name=Tier2 type=fanout durable=true internal=true
rabbitmqadmin declare exchange name=Tier3 type=fanout durable=true internal=true
rabbitmqadmin declare exchange name=Tier4 type=fanout durable=true internal=true

#read users from conf file and fill arrays
config_file="users.yaml"
users_array=()
write_tier_array=()
read_tier_array=()

USERS=$(rabbitmqadmin list users name -f tsv)

while IFS= read -r line || [[ -n "$line" ]]; do

  if [[ "$line" =~ ^[[:space:]]*name[[:space:]]*:[[:space:]]*(.*)$ ]]; then
    users_array+=("${BASH_REMATCH[1]}")
  fi

  if [[ "$line" =~ ^[[:space:]]*write[[:space:]]*:[[:space:]]*(.*)$ ]]; then
    write_tier_array+=("${BASH_REMATCH[1]}")
  fi

  if [[ "$line" =~ ^[[:space:]]*read[[:space:]]*:[[:space:]]*(.*)$ ]]; then
    read_tier_array+=("${BASH_REMATCH[1]}")
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
    #personal queue 
  rabbitmqadmin declare queue name=${users_array[$user]}

    #writing permission on default exchange with its route key and reading permission on its queue
  rabbitmqctl set_permissions -p / ${users_array[$user]} "\$" "^(DefaultPeerRequest)\$" "^(${users_array[$user]})\$"

    #setting message routing to tiers (BINDING EXCHANGE TO EXHANGE)
  rabbitmqadmin declare binding source="DefaultPeerRequest" destination="${write_tier_array[$user]}" routing_key="${users_array[$user]}" destination_type="exchange"

    #setting queues filling from tiers (BINDING EXCHANGE TO QUEUE)
  rabbitmqadmin declare binding source="${read_tier_array[$user]}" destination="${users_array[$user]}"
    #certificates generation
  if [[ "$FOUND" -eq 0 ]]; then
    ./cert_gen.sh ${users_array[$user]}
  fi
done
