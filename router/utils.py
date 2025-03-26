
import config
import ssl
from filelock import FileLock
import pika
import logging

ssl_context = ssl.create_default_context(cafile=config.ca_cert)
ssl_context.load_cert_chain(certfile=config.agent_cert, keyfile=config.agent_key)

connection_params = pika.ConnectionParameters(
    config.host,
    ssl_options=pika.SSLOptions(context=ssl_context),
    credentials=pika.credentials.ExternalCredentials(),
)

publisher_conn = pika.BlockingConnection(connection_params)
publisher_channel = publisher_conn.channel()

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

metric_log = logging.getLogger("metric_logger")
metric_handler = logging.FileHandler(config.metrics_file)
metric_handler.setLevel(logging.DEBUG)
metric_handler.setFormatter(formatter)
metric_log.addHandler(metric_handler)

rule_log = logging.getLogger("rule_logger")
rule_handler = logging.FileHandler(config.rules_file)
rule_handler.setLevel(logging.DEBUG)
rule_handler.setFormatter(formatter)
rule_log.addHandler(rule_handler)
