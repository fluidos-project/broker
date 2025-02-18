<!-- markdownlint-disable first-line-h1 -->
<p align="center">
<a href="https://www.fluidos.eu/"> <img src="./docs/images/fluidoslogo.png" width="150"/> </a>
<h3 align="center">FLUIDOS Broker</h3>
</p>  

# WAN Discovery – RabbitMQ Configuration Guide

This repository provides an example of configuration to set up a RabbitMQ message broker for WAN-based discovery of FLUIDOS Nodes.

## Prerequisites

A vanilla RabbitMQ installation is required on your server.  
Refer to the official <a href="https://www.rabbitmq.com/docs/configure"> RabbitMQ Configuration </a> to determine the correct location of the rabbitmq.conf file based on your system.

The provided `rabbitmq.conf` configuration enforces TLS peer authentication for both client and server communications. It configures RabbitMQ to use the default SSL port 5671 and disables the non-SSL TCP port 5672. The configuration also sets the Common Name (CN) of the SSL certificate as the authentication ID, additionally, it restricts access to the Management UI and `rabbitmqadmin` tools to localhost, enhancing the system’s security by limiting administrative access to the local machine only.  
To enable TLS-based authentication, activate the RabbitMQ TLS authentication plugin:  
`rabbitmq-plugins enable rabbitmq_auth_mechanism_ssl`

## Certificate Issuance

To enable TLS-based authentication, you must generate the self-signed root certificate and a server certificate issued by the root certificate.  
We use RSA 2048-bit encryption, and example configurations are provided below.

    openssl req -x509 -newkey rsa:2048 -keyout CA_privKey.pem -out CA_cert.pem -days 365 -config CA.conf

    openssl x509 -req -in serverCert/server.csr -CA CAcert/CA_cert.pem -CAkey CAcert/CA_privKey.pem -CAcreateserial -out serverCert/server_cert.pem -days 365 -sha256 -extfile serverCert/server.conf -extensions v3_req


## User & Queue Configuration

Some scripts rely on `rabbitmqadmin`, so ensure that an administrator user is properly configured and that the default "guest" user is restricted to localhost access only.  
  
From the `users.yaml` configuration, clients publish to the same exchange but use distinct routing keys, which correspond to their Common Name (CN) in their certificate.
These routing keys determine message distribution across tiers (which act as exchanges).
Each client is subscribed to its own private queue, which receives messages routed from the relevant tiers.  
  
The `setup.sh` script automates the setup of queues, permissions, exchanges, and bindings as defined in `users.yaml`.
Client certificates and private keys, ensuring each client can authenticate securely.  
  
The `eraseRabbit.sh` script removes all queues, bindings, exchanges, and users, except for the default "guest" user, ensuring continued access via `rabbitmqadmin`.  
  
The `deleteUserBindings.sh` script removes all the bindings for the user passed as argument.  
  
Once the setup is over it it is possible to refine the configuration with specific `rabbitmqctl` and `rabbitmqadmin` commands to create more bindings.  
Previously issued certificates will continue to function as expected.  

## Message Routing & Permissions

Each client can publish only using its assigned routing key to the defaultPeeringExchange and can subscribe only to its private queue.  
Clients are categorized into four arbitrary tiers for message routing.

### A simple schema that illustrates a possible broker architecture

<p align="center">
<img src="./docs/images/broker_server.jpg"/>
</p>

## Directory structure example compatible for setup.sh

    ~/
    ├─ CAcert/
    │  ├─ CA.conf
    │  ├─ CA_privKey.pem
    │  ├─ CA_cert.pem
    ├─ clientCert/
    │  ├─ clientA_priv.pem
    │  ├─ clientA_cert.pem
    │  ├─ clientB_priv.pem
    │  ├─ clientB_cert.pem
    │  ├─ client.conf
    │  ├─ clientA_request.csr
    │  ├─ clientB_request.csr
    ├─ serverCert/
    │  ├─ server_cert.pem
    │  ├─ server_privKey.pem
    │  ├─ server.conf
    │  ├─ server.csr
    ├─ users.yaml
    ├─ setup.sh
    ├─ cert_gen.sh
    ├─ eraseRabbit.sh
