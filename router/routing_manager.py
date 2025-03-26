import pika
import json
from datetime import datetime
import config
import utils

class RoutingManager:
    def __init__(self):
        self.input_queue = 'announcements_queue'
        self.output_exchange = 'routing_exchange'
        metrics = ""

    def check_api(self, client):
        """Verify permissions on ERP"""
        # Your code here
        return True

    # def update_metrics(self, client_name, ip):
    #     """Update metrics for new client publishing"""
    #     metrics = utils.load_yaml_with_lock(config.metrics_file, config.metrics_lock_file)
    #     found = False

    #     for entry in metrics:
    #         if client_name in entry:
    #             entry[client_name]['ip'] = ip
    #             utils.save_yaml_with_lock(config.metrics_file, config.metrics_lock_file, metrics)
    #             found = True
    #             break
    #     if not found:
    #         metrics.append({client_name: {'ip': ip, 'latency': None, 'throughput': None, 'zone': None}})
    #         utils.save_yaml_with_lock(config.metrics_file, config.metrics_lock_file, metrics)
    #         print(f"[@] New client added {client_name} IP: {ip}")


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
        """Build the routing key from metrics and rule requirements"""

        routing_parts = []
        for rule in config.requirements_array:

            print(f"RULE {rule}")
            print(f"MESSAGE {message}")


            if not self.check_api(rule["sender"]):
                print(f"API failed {rule["sender"]}")
                continue
            #verify that all the keys of the rule are contained in the message
            subset_keys_ok = rule.keys()<=message.keys()
            latency_ok = int(rule["MAXlatency"]) >= int(message['latency'])
            bandwidth_ok = int(rule["MINbandwidth"]) <= int(message['bandwidth'])

            for location in rule["locations"]:
                location_ok = location == message["location"]
                if location_ok: break

            if latency_ok and bandwidth_ok and location_ok: #and subset_keys_ok:
                routing_parts.append(rule["sender"])
                break
        return '.'.join(routing_parts)


    def callback(self, ch, method, properties, body):
        """Callback."""
        try:
            sender = properties.user_id
            message = json.loads(body)
            message["sender"]=sender

            routing_key = self.forge_routingkey(message)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            utils.publisher_channel.basic_publish(exchange=self.output_exchange, routing_key=routing_key, body=body)
            current_time = datetime.now()
            print(f"[@] ROUTING {current_time} Sender: {sender} - Received: {message} - Routing Key: {routing_key}")
            utils.metric_log.info(json.dumps(message))
            #utils.metric_log.flush() 
        except Exception as e:
            print(f"[@] Error in announcements callback: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


    def start(self):
        """Subscrition to queue."""
        consumer_conn = pika.BlockingConnection(utils.connection_params)
        consumer_channel = consumer_conn.channel()
        consumer_channel.queue_declare(queue=self.input_queue, durable=True)
        consumer_channel.basic_consume(queue=self.input_queue, on_message_callback=self.callback)

        print("[@] Waiting for new announcements...")
        consumer_channel.start_consuming()
