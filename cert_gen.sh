#!/usr/bin/bash

#1-create key and csr
openssl req -new -newkey rsa:2048 -nodes -keyout clientCert/"$1"_priv.pem -config clientCert/client.conf -out clientCert/"$1"_request.csr -subj "/CN="$1""
#2-sign
openssl x509 -req -in clientCert/"$1"_request.csr -CA CAcert/CA_cert.pem -CAkey CAcert/CA_privKey.pem -CAcreateserial -out clientCert/"$1"_cert.pem -days 365 -extfile clientCert/client.conf -extensions v3_req