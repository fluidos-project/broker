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


    def callback(self, ch, method, properties, body):
        """Callback."""
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
            print(f"[@] Error in rules callback: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


    def start(self):
        """Subscrition to queue."""

        consumer_conn = pika.BlockingConnection(utils.connection_params)
        consumer_channel = consumer_conn.channel()
        consumer_channel.queue_declare(queue=self.input_queue, durable=True)
        consumer_channel.basic_consume(queue=self.input_queue, on_message_callback=self.callback, auto_ack=False)

        print("[@] Waiting for new rules...")
        consumer_channel.start_consuming()
