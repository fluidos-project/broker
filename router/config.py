prefix_dir = ".."
log_file = f"logs/broker_messages.log"
client_cert_dir = f"{prefix_dir}/clientCert"
ca_cert = f"{prefix_dir}/CAcert/CA_cert.pem"
agent_cert = f"{client_cert_dir}/broker_router_cert.pem"
agent_key = f"{client_cert_dir}/broker_router_priv.pem"
host = "fluidos.top-ix.org"
comparator_module_path="metrics_comparators"
port=5671
rules_array = []
