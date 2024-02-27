.. _networking:

Network Configuration
=============================

DNS
--------------------
You should register your server's IP address with your DNS provider. This will allow you to access your server using a domain name.

Ports
--------------------

Below is a description of the ports used by the different services being run in the docker swarm.

* Montreal is working with Ubuntu. `Installation of docker <https://docs.docker.com/engine/install/ubuntu/>`_
* `Installation of docker compose <https://docs.docker.com/compose/install/linux/>`_

* Gitlab: 
    * SSH: 222:22
    * HTTP: 80:80
    * HTTPS: 443:443
    * Registry: 5000:5000
* Gitlab-runner:
    * Gitlab communication (TLS): 8093:8093    
* StoreSCP:
    * DICOMs (any valid tcp/ip port can be specified): 2100:2100    
* MinIO:
    * 9000:9000
    * 9090:9090    
* Docker Swarm:
    * TCP port 2377 for cluster management communications
    * TCP and UDP port 7946 for communication among nodes
    * UDP port 9789 for overlay network traffic

