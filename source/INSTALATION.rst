.. _software-stack-deployment:

Software Stack Deployment
---------------------

This page will go through the sofware stack installation and how to get started. 

As explained in the :ref:`hardware requirements <hardware-requirements>` section, the BIDS-flux infrastructure recommends using two local servers to ensure secure and efficient functionality. One server should have ample storage and moderate compute power, while the other should have limited storage but high computational power. The centralized server should have robust storage and sufficient computational power to handle data from all sites.

Both local and centralized infrastructures will rely on the `docker <https://docs.docker.com/>`_ engine, specifically using `docker-compose <https://docs.docker.com/compose/>`_ and `docker swarm mode <https://docs.docker.com/engine/swarm/swarm-mode/>`_ to run the services. Super user permissions will be required. Additionally, both local and centralized servers/VMs will use git for version control. Doker swarm mode was selected to take advantage of the built-in secret features and the ability to scale services across multiple servers.

Install Docker on all servers/VMs by following the official Docker documentation for your specific Linux distribution: `install docker <https://docs.docker.com/engine/install/ubuntu/>`_ and `docker compose <https://docs.docker.com/compose/install/linux/>`_. You can verify the installation with the following command:

.. code-block:: bash

    docker --version
    docker run hello-world

Install Git in all the servers/VMs. Follow the official git documentation to `install git <https://git-scm.com/doc>`_ for your correct linux distribution. You can run the following command to check if git is installed correctly:

.. code-block:: bash

    git --version

Local Infrastructure
^^^^^^^^^^^^^^^^^^^^

Each local server/VM will need to have docker engine running and should have initalized a docker swarm. On the data server you will run the follwoing command to initialize the swarm:

.. code-block:: bash

    docker swarm init

You will receive a token that you can use to join the processing server to the swarm. 

.. note:: 

    Make sure that you newtork is configured correctly and that the data and processing servers/VMs can communicate with each other on the required ports by docker https://docs.docker.com/engine/swarm/swarm-tutorial/#open-protocols-and-ports-between-the-hosts.

.. code-block:: bash

    Swarm initialized: current node (dxn1zf6l61qsb1josjja83ngz) is now a manager.

    To add a worker to this swarm, run the following command:

        docker swarm join \
        --token SWMTKN-1-49nj1cmql0jkz5s954yi3oex3nedyz0fb0xx14ie39trti4wxv-8vxv8rssmk743ojnwacrr2e7c \
        192.168.99.100:2377

    To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.

As indicated previously you will need to run the following command on the processing server:

.. code-block:: bash

    docker swarm join --token <token> <ip>:2377



Once you have Docker and Git installed, you can start deploying the services. You will need to clone the git repository which contains the docker-compose yaml files to deploy the services.

.. code-block:: bash

    git clone https://github.com/BIDS-flux/BIDS-flux.git






Centralized Infrastructure
^^^^^^^^^^^^^^^^^^^^^^^^^^
