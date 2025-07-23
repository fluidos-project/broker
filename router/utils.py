
import config
import ssl
import pika
import logging

ssl_context = ssl.create_default_context(cafile=config.ca_cert)
ssl_context.load_cert_chain(certfile=config.agent_cert, keyfile=config.agent_key)

connection_params = pika.ConnectionParameters(
    config.host,
    ssl_options=pika.SSLOptions(context=ssl_context),
    credentials=pika.credentials.ExternalCredentials(),
    heartbeat=60,
    blocked_connection_timeout=120,
)

logging.basicConfig(
    filename=config.log_file,
    level=logging.INFO,  # (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

