import pika
import json
from datetime import datetime
import utils
import config


class RulesManager:
    def __init__(self):
        self.input_queue = 'rules_queue'
        self.exchange = 'routing_exchange'


    def update_rules(self, message):
        """Update rules."""

        for rule in config.rules_array:
            if message["sender"] == rule["sender"]:
                config.rules_array.remove(rule)
        config.rules_array.append(message)
        #print(f"[@] Added {message}")


    def callback(self, ch, method, properties, body):
        try:
            """Update rules_array with the new rule."""
            sender = properties.user_id
            current_time = datetime.now()

            data = json.loads(body)
            #nested JSON
            while(type(data)!=dict):
                data = json.loads(data)

            data["sender"] = sender
            print(f"[@] RULES {current_time} New rule received: {data}")
            self.update_rules(data)
            utils.logging.info(f"RULE {json.dumps(data)}")

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
