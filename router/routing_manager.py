import pika
import json
from datetime import datetime
import config
import utils
import importlib

class RoutingManager:
    def __init__(self):
        self.input_queue = 'announcements_queue'
        self.output_exchange = 'routing_exchange'


    def check_api(self, client):
        """Verify permissions on ERP"""
        # Your code here
        return True


    def update_metrics(self, client_name, body):
        """Update metrics for new client publishing"""
        found = False
        for entry in config.metrics_array:
            if client_name in entry:
                entry[client_name] = body
                found = True
                break
        if not found:
            config.metrics_array.append({client_name: {body}})
            print(f"[@] New client added {client_name} Body: {body}")
    

    def forge_routingkey(self, message):
        """Build the routing key from metrics and rules requirements"""

        routing_parts = []
        for rule in config.rules_array:
            #print(f"RULE {rule}")
            #print(f"MESSAGE {message}")
            result=True
            for key in rule.keys():
                module_name = f"{config.comparator_module_path}.{key}"
                # Dinamic Import
                try:
                    comparator_module = importlib.import_module(module_name)
                except ModuleNotFoundError:
                    #if metric in rule has not comparator use default
                    comparator_module = importlib.import_module(f"{config.comparator_module_path}.default")
                result = result and (comparator_module.comparator.compare(rule[key], message))
            if result:
                routing_parts.append(rule.get("sender"))

        return '.'.join(routing_parts)


    def callback(self, ch, method, properties, body):
        """Callback."""
        try:
            sender = properties.user_id
            
            message = json.loads(body)
                #nested JSON
            while(type(message)!=dict):
                message = json.loads(message)

            message["sender"]=sender
            #ch.basic_ack(delivery_tag=method.delivery_tag)
            routing_key = self.forge_routingkey(message)
            properties = pika.BasicProperties(expiration='30000')
            utils.publisher_channel.basic_publish(exchange=self.output_exchange, routing_key=routing_key, body=body, properties=properties)
            current_time = datetime.now()
            print(f"[@] ROUTING {current_time} Sender: {sender} - Received: {message} - Routing Key: {routing_key}")
            utils.logging.info(f"ROUTING {json.dumps(message)}")

        except Exception as e:
            print(f"[@] Error in announcements callback: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


    def start(self):
        """Subscrition to queue."""
        
        #while True:
            #try:
        consumer_conn = pika.BlockingConnection(utils.connection_params)
        consumer_channel = consumer_conn.channel()
        consumer_channel.queue_declare(queue=self.input_queue, durable=True)
        consumer_channel.basic_consume(queue=self.input_queue, on_message_callback=self.callback, auto_ack=True)

        print("[@] Waiting for new announcements...")
        consumer_channel.start_consuming()

            #except Exception as e:
            #    print(f" [!] Error: {e}. Restarting in 5 seconds")
            #    time.sleep(2)