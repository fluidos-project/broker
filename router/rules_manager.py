import pika
import json
from datetime import datetime
import utils
import config

import os
import stat

class RulesManager:
    def __init__(self):
        self.input_queue = 'rules_queue'
        self.exchange = 'routing_exchange'


    def update_rules(self, message):
        """Update rules."""

        for rule in config.requirements_array:
            if message["sender"] == rule["sender"]:
                config.requirements_array.remove(rule)
        config.requirements_array.append(message)
        print(f"[@] Added {message}")



    # def generate_requirements(self, rule):
    #     """Create rules for routing key."""

    #     latency = rule.get('latency')
    #     bandwidth = rule.get('bandwidth')
    #     locations = rule.get('locations', [])

    #     for location in locations:
    #         config.requirements_array.append(latency+"."+bandwidth+"."+location)
    #     # parts = rule.split('.')
    #     # if '-' not in parts[2]:
    #     #     return [rule]
    #     # prefix = '.'.join(parts[:2])
    #     # suffixes = parts[2].split('-')
    #     #return [f"{prefix}.{suffix}" for suffix in suffixes]


    def callback(self, ch, method, properties, body):
        try:
            """Update file YAML with new rules and create binding."""
            sender = properties.user_id
            current_time = datetime.now()

            data = json.loads(body)
            #nested JSON
            data = json.loads(data)
            data["sender"] = sender
            print(f"[@] Inbound RULE {current_time} New rule received: {data}")
            self.update_rules(data)

            utils.rule_log.info(str(data))
            utils.rule_handler.flush()



            #utils.rule_log.flush() 
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"[@] Error in rule message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


    def start(self):
        """Queue subscription."""
        connection = pika.BlockingConnection(utils.connection_params)
        channel = connection.channel()

        channel.queue_declare(queue=self.input_queue, durable=True)
        channel.basic_consume(queue=self.input_queue, on_message_callback=self.callback)

        print("[@] Witing for new rules...")
        channel.start_consuming()
