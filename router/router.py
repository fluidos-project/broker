import pika
import yaml
import json
import ssl
from datetime import datetime
from filelock import FileLock

prefix_dir="/home/topix"
ssl_context = ssl.create_default_context(cafile=prefix_dir+"/CAcert/CA_cert.pem")
ssl_context.load_cert_chain(certfile=prefix_dir+"/clientCert/localAgent_cert.pem", keyfile=prefix_dir+"/clientCert/localAgent_priv.pem")
metrics_file = prefix_dir+'/router/metrics.yaml'
rules_file = prefix_dir+'/router/routingRules.yaml'
metrics_lock_file = metrics_file + ".lock" 
host='fluidos.top-ix.org'

connection_params = pika.ConnectionParameters(
    host,#='fluidos.top-ix.org',#localhost
    port=5671,
    ssl_options=pika.SSLOptions(context=ssl_context),
    credentials=pika.credentials.ExternalCredentials(),
    
)

class RoutingManager:
    def __init__(self, rabbitmq_host=host):#localhost
        self.rabbitmq_host = rabbitmq_host
        self.input_queue = 'announcements_queue'
        self.output_exchange = 'routing_exchange'
        self.metrics_file = metrics_file

    def load_metrics(self):
        """Read metrics"""
        lock = FileLock(metrics_lock_file)
        try:
            with lock.acquire(timeout=5): #acquiring wait
                with open(metrics_file, 'r') as file:
                    data = yaml.safe_load(file)
                    return data if data else []
        except Exception as e:
            print(f"Errorloading metrics: {e}")
        return []

    
    def save_metrics(self, data):
        """Write metrics"""
        lock = FileLock(metrics_lock_file)
        try:
            with lock.acquire(timeout=5):
                with open(metrics_file, 'w') as file:
                    yaml.dump(data, file)
        except Exception as e:
            print(f"Error writing metrics: {e}")


    def save_rules(self, rules):
        """Saves rules in YAML."""
        with open(self.rules_file, 'w') as file:
            yaml.safe_dump(rules, file)

    def generate_routing_key(self, sender):
        """Retrieves routing key from metrics."""
        metrics = self.load_metrics()

        for entry in metrics:
            if sender in entry:
                data = entry[sender]
                return f"{data['latency']}.{data['throughput']}.{data['zone']}"

        return "default.key"
    

    def update_metrics(self, client_name, ip):
        """Update metrics if client is new"""
        metrics = self.load_metrics()
        found = False

        for entry in metrics:
            if client_name in entry:
                entry[client_name]['ip'] = ip
                self.save_metrics(metrics)
                found = True
                break
        if not found:
            metrics.append({client_name: {'ip': ip, 'latency': None, 'throughput': None, 'zone': None}})
            self.save_metrics(metrics)
            print(f"[@] Client added {client_name} IP: {ip}")


    def callback(self, ch, method, properties, body):
        """Creates new routing key."""
        sender = properties.user_id
        message = json.loads(body)
        self.update_metrics(sender, message['ip'])
        routing_key = self.generate_routing_key(sender)

        current_time = datetime.now()
        print(f"[@] ROUTING {current_time} Received: {message} - Sender: {sender} - Routing Key: {routing_key}")

        ch.basic_publish(exchange=self.output_exchange, routing_key=routing_key, body=body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        """Queue subscription"""
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()

        channel.queue_declare(queue=self.input_queue, durable=True)
        channel.exchange_declare(exchange=self.output_exchange, exchange_type='topic', durable=True)

        channel.basic_consume(queue=self.input_queue, on_message_callback=self.callback)

        print("[@] Waiting for messages...")
        channel.start_consuming()


class RulesManager:
    def __init__(self, rabbitmq_host=host):#localhost
        self.rabbitmq_host = rabbitmq_host
        self.input_queue = 'rules_queue'
        self.rules_file = rules_file
        self.exchange = 'routing_exchange'
        self.metrics_file = metrics_file


    def load_rules(self):
        """Loads rules from YAML."""
        with open(self.rules_file, 'r') as file:
            return yaml.safe_load(file)


    def save_rules(self, rules):
        """Saves rules in YAML."""
        with open(self.rules_file, 'w') as file:
            yaml.safe_dump(rules, file)

        
    def load_metrics(self):
        """Read metrics with lock"""
        lock = FileLock(metrics_lock_file)
        try:
            with lock.acquire(timeout=5):  # max wait if file is busy
                with open(metrics_file, 'r') as file:
                    data = yaml.safe_load(file)
                    return data if data else []
        except Exception as e:
            print(f"Error loading metrics: {e}")
        return []


    def create_bindings(self, channel, sender, binding_keys):
        """Creates bindings for RabbitMQ."""
        metrics = self.load_metrics()
        for key in binding_keys:
            
            for metric in metrics:
                #print(f"[@] Evaluate metric {metric}")
                client_data = list(metric.values())[0]
                #print(f"[@] ClientData {client_data}")
                parts = key.split('.')
                #print(f"[@] Evaluate key {key}")
                #print(f"[@] intKey0 {int(parts[0])} >= latency {int(client_data['latency'])}")
                #print(f"[@] intKey1 {int(parts[1])} <= through {int(client_data['throughput'])}")
                #print(f"[@] intKey2 {parts[2]} == zone {client_data['zone']}")
                if(client_data['ip'] == 'null'): 
                    break
                elif((int(parts[0]) >= int(client_data['latency'])) and (int(parts[1]) <= int(client_data['throughput'])) and (parts[2] == client_data['zone'])):
                    channel.queue_bind(exchange=self.exchange, queue=sender, routing_key=key)
                    print(f"[@] Binding created: {sender} -> {self.exchange} ({key})")


    def update_rules(self, binding_keys, sender):
        """Updates rules."""
        rules = self.load_rules()
        updated = False
        for rule in rules:
            if sender in rule:
                rule[sender]['requirements'] = binding_keys
                updated = True
                break

        if not updated:
            rules.append({sender: {'name': sender, 'requirements': binding_keys}})

        self.save_rules(rules)
        print(f"[@] Rules updated for {sender} with routing key {binding_keys}")


    def checkApi(self):
        """Check if the rules are allowed business side."""
        #your code here
        return True
    

    def generate_binding_keys(self, rule):
        """Creates routing keys from rule"""
        parts = rule.split('.')
    
        if '-' not in parts[2]:
            return [rule]
        prefix = '.'.join(parts[:2])  # A.B
        suffixes = parts[2].split('-')  # [C, D, E]
    
        return [f"{prefix}.{suffix}" for suffix in suffixes]

    
    def callback(self, ch, method, properties, body):
        """Update file YAML with new rules and create binding."""
        sender = properties.user_id
        new_rule = json.loads(body)
        current_time = datetime.now()
        print(f"[@] RULES {current_time} New rule received: {new_rule}")
        binding_keys=self.generate_binding_keys(new_rule)
        self.update_rules(binding_keys, sender)
        if self.checkApi():
          self.create_bindings(ch, sender, binding_keys)
        ch.basic_ack(delivery_tag=method.delivery_tag)


    def start(self):
        """Queue subscription."""
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()

        channel.queue_declare(queue=self.input_queue, durable=True)
        channel.basic_consume(queue=self.input_queue, on_message_callback=self.callback)

        print("[@] Witing for new rules...")
        channel.start_consuming()


if __name__ == "__main__":
    import threading

    routing_manager = RoutingManager()
    rules_manager = RulesManager()

    thread1 = threading.Thread(target=routing_manager.start)
    thread2 = threading.Thread(target=rules_manager.start)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
