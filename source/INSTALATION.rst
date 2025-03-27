.. _software-stack-deployment:

Software Stack Deployment
---------------------

This page will go through the sofware stack installation and how to get started. 

As explained in the :ref:`hardware requirements <hardware-requirements>` section, the BIDS-flux infrastructure recommends using two local servers to ensure secure and efficient functionality. One server should have ample storage and moderate compute power, while the other should have limited storage but high computational power. The centralized server should have robust storage and sufficient computational power to handle data from all sites.

Both local and centralized infrastructures will rely on the `docker <https://docs.docker.com/>`_ engine, specifically using `docker-compose <https://docs.docker.com/compose/>`_ and `docker swarm mode <https://docs.docker.com/engine/swarm/swarm-mode/>`_ to run the services. Super user permissions will be required. Additionally, both local and centralized servers/VMs will use git for version control. Doker swarm mode was selected to take advantage of the built-in secret features and the ability to scale services across multiple servers.

Install Docker on all servers/VMs by following the official Docker documentation for your specific Linux distribution: `install docker <https://docs.docker.com/engine/install/ubuntu/>`_ and `docker compose <https://docs.docker.com/compose/install/linux/>`_. You can verify the installation with the following command:

.. code-block:: bash

    sudo docker --version
    sudo docker run hello-world

Install Git in all the servers/VMs. Follow the official git documentation to `install git <https://git-scm.com/doc>`_ for your correct linux distribution. You can run the following command to check if git is installed correctly:

.. code-block:: bash

    git --version

Local Infrastructure
^^^^^^^^^^^^^^^^^^^^

Each local server/VM will need to have docker engine running and should have initalized a docker swarm. On the data server you will run the following command to initialize the docker swarm. The recommended breakdown is to use two servers and divide the services as follows:

   #. Data Server:

        a. GitLab  
        b. GitLab - Runner (Docker-in-Docker)  
        c. MinIO  
        d. Mercure / StoreSCP

   #. Processing Server:

        a. GitLab Runner

#. Create a ``docker swarm manager node`` in the ``Data Server``.

    .. code:: bash

        docker swarm init --dport 9789

    .. code-block:: bash

        Swarm initialized: current node (dxn1zf6l61qsb1josjja83ngz) is now a manager.

        To add a worker to this swarm, run the following command:

            sudo docker swarm join \
            --token SWMTKN-1-49nj1cmql0jkz5s954yi3oex3nedyz0fb0xx14ie39trti4wxv-8vxv8rssmk743ojnwacrr2e7c \
            --advertise-addr 192.168.99.100:2377

        To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.

    .. warning::
        
        Be aware of the issues with docker swarm in a `VMWare virutal machine <https://portal.portainer.io/knowledge/known-issues-with-vmware>`_.

    .. note:: 

        Make sure that you newtork is configured correctly and that the data and processing servers/VMs can communicate with each other on the required ports by docker https://docs.docker.com/engine/swarm/swarm-tutorial/#open-protocols-and-ports-between-the-hosts.


#. Go into the worker node (``processing server``) and run the following command with the information obtained from the previous command.

    .. code:: bash

        docker swarm join --token TOKEN --advertise-addr <IP-ADDRESS-OF-WORKER-1> <IP-ADDRESS-OF-MANAGER>:2377

#. Create an attachable docker overlay network. This network will be used by all the services to securely communicate.

    .. code:: bash

        docker network create --driver=overlay --attachable BIDS-flux-net --gateway=192.11.0.2


#. Once you have Docker, Git installed, and the docker swarm configured, you can start deploying the services. You will need to clone the software stack git repository which contains the docker-compose yaml files to deploy the services into the manager node in this case this will be the ``data server``.

    .. code-block:: bash

        git clone https://gitlab.unf-montreal.ca/bids-flux/local-stack.git

#. Also clone the following repositories for the deployment:

    .. code-block:: bash

        git clone https://gitlab.unf-montreal.ca/bids-flux/containers.git
        git clone https://gitlab.unf-montreal.ca/bids-flux/ci-pipelines.git


#. The deployment of the services will be mostly automatic providing the correct configurations, nevertheless, there will still be some manual configurations that will reguire careful attention.


.. _local-configuration-stage1:

Configuration Stage 1
~~~~~~~~~~~~~~~~~~~~~

#. Change directory into the cloned repository and follow the next steps.

    .. code-block:: bash
        
        cd local-stack


#. The ``.env`` file will need to be set up with the proper domain names of the Docker Swarm nodes where the individual services will be deployed. Once again, for BIDS-flux, the recommended breakdown is:

    Data Server: GitLab, GitLab - Runner (Docker-in-Docker), MinIO, Mercure / StoreSCP

    Processing Server: GitLab Runner

    .. code-block:: bash

        # This is an example of what you will want to configure
        DOMAIN_NAME=data-server.org
        DICOM_ENDPOINT_HOST=data-server.org
        GITLAB_HOST=data-server.org
        STORAGE_SERVER_HOST=data-server.org
        PROC_SERVER_HOST=proc-server.org

#. The ``.env`` file also contains information regarding the directory were the gitlab will be storing all its data.

    .. code-block:: bash

        # This location is usually standard but feel free to modify is required
        GITLAB_HOME=/srv/gitlab

#. If you are using the recommended Mercure you will require to configure some fields of the ``config/mercure-conf/default_mercure.json``. 

    #. The `Modules` field in the json file to properly point to the dicom-indexer image.
    #. The environment variables to be used for this containers. 
    #. The docker arguments including the docker command to run. 
    #. Any necessary directory bindings for this container.

    .. note::

        This step can be manually finetunned using the `Mercure GUI` once Mercure has been installed.
        
    .. note::

        You may have noticed that the mercure service is not included in the `` BIDSflux-stack.yml`` file, this is okay. Mercure needs to be installed using `docker-compose` as oposed to `docker swarm`, but don't worry, we will install it right after. 

.. _local-stack-deployment-stage1:

Stack Deployment Stage 1
~~~~~~~~~~~~~~~~~~~~~~~~

#. One you have completed the initial configuration, we need to deploy de secrets for the docker-warm services by running the ``deploy/generate_secrets.sh``

    .. code-block:: bash
        
        bash deploy/generate_secrets.sh

#. You will need to run the following command to initiate the docker swarm for the BIDSflux infraestructure. This will create a new docker stack where the docker swarm services will be deployed.

    .. code-block:: bash
        
        sudo docker stack deploy -c BIDSflux_stack.yml BIDSflux

    .. note::

        It takes some time to finish up downloading the images and deploying the services.

    You can confirm the docker stack initialization by checking the services.

    .. code-block:: bash

        sudo docker services ls

    This should return some information of the deployment status, for exapmle, the gitlab service.

    .. code-block:: bash

        ID             NAME                      MODE         REPLICAS   IMAGE                                                                             PORTS
        jhyou70vh0zz   BIDSflux_gitlab               replicated   1/1        gitlab/gitlab-ee:17.7.1-ee.0                                                      *:80->80/tcp, *:222->22/tcp, *:443->443/tcp, *:5050->5050/tcp

    What we care about the most is the REPLICAS as it tells us how many of the asked deployments are successfully up and running. You can also run the following command to get the service logs.

    .. code-block:: bash

        sudo docker service logs BIDSflux_gitlab

    .. note::

        If you see REPLICAS as 0/1 this means that your deployment is in place or there was an error with the deployment. You can get more information using the following command:

        .. code-block:: bash

            sudo docker stack ps BIDSflux --no-trunc | grep <Service with 0/1 replicas>



#.  You have all BIDSflux services running with 1/1 replicas, it is time to move to the next configuration stage.


.. _local-configuration-stage2:

Configuration Stage 2
~~~~~~~~~~~~~~~~~~~~~

#. Run the ``mercure-setup.sh`` script in preparation for the Mercure deployment.

#. Get token variables.

#. Register runners.

#. If you are using storescp instead of mercure you will need to properly configure these ``.env`` variables.

    .. code-block:: bash

        # Required if you are using storescp an not mercure, if using mercure these will be configured someplace else
        GITLAB_REGISTRY_PATH=registry.gitlab.${DOMAIN_NAME}/ni-dataops/containers
        S3_URL_PATTERN='s3://s3.data-server.org/test.{ReferringPhysicianName}.{StudyDescriptionPath[1]}.dicoms'
        GITLAB_INDEXER_GROUP_TEMPLATE="{ReferringPhysicianName}/{StudyDescriptionPath[1]}"

    And you will use BIDS-flux the following lines in the ``BIDS-flux.yml`` file corresponding to the service deployment.

    .. code-block:: bash

        # # this service requires:
        # # - gitlab instance to be started
        # # - deploy to be run to have containers repo fork
        # # - ni-dataops/containers to have completed containers build so that image below is in registry
        # dicom_endpoint:
        #   image: ${GITLAB_REGISTRY_PATH}/dicom_indexer:latest
        # #  hostname: storescp
        # #  profiles: [dicom_endpoint]
        #   depends_on: [gitlab, gitlab-runner-proc]
        #   environment:
        #     CI_SERVER_HOST: $CI_SERVER_HOST
        #     GITLAB_BOT_USERNAME: $GITLAB_BOT_USERNAME
        #     GITLAB_BOT_EMAIL: $GITLAB_BOT_EMAIL
        #     STORESCP_AET: $STORESCP_AET
        #     GITLAB_INDEXER_GROUP_TEMPLATE: "{ReferringPhysicianName}/{StudyDescriptionPath[1]}"
        #     S3_URL_PATTERN: 's3://s3.data-server.org/test.{ReferringPhysicianName}.{StudyDescriptionPath[1]}.dicoms'
        #   networks:
        #     - BIDS-flux-net
        #   secrets:
        #     - source: dicom_bot_token
        #       target: /var/run/secrets/dicom_bot_gitlab_token
        #     - source: s3_id
        #       target: /var/run/secrets/s3_id
        #     - source: s3_key
        #       target: /var/run/secrets/s3_secret

        #   ports:
        #     - "$STORESCP_PORT:$STORESCP_PORT"
        #   deploy:
        #     placement:
        #       constraints:
        #         - node.hostname == $DICOM_ENDPOINT_HOST
        #   entrypoint: ["/usr/bin/storescp", "-aet", "$STORESCP_AET", "-pm", "-od", "/tmp", "-su", "", "--eostudy-timeout", "60", "--exec-on-eostudy", "python indexer/index_dicom.py", "--gitlab-url $CI_SERVER_HOST", "--storage-remote", '$S3_URL_PATTERN', "--gitlab-group-template", '$GITLAB_INDEXER_GROUP_TEMPLATE', '#p', '$STORESCP_PORT']

.. _local-stack-deployment-stage2:

Stack Deployment Stage 2
~~~~~~~~~~~~~~~~~~~~~~~~

#. you can now deploy `Mercure` and you can do so with a simple command.

    .. code-block:: bash

        # Here the -f tells docker compose which file to use, -d tells docker to run in detached mode, and up is the command to deploy the mercure services    
        sudo docker compose -f docker-compose-mercure.yml up -d

#. if you are using storescp then re-run the command:

    .. code-block:: bash
        
        sudo docker stack deploy -c BIDSflux_stack.yml BIDSflux

#. Run the ``deploy/init_ni-dataops.py``

    .. code-block:: bash
        
        python deploy/init_ni-dataops.py deploy/ci_variables.json 

Centralized Infrastructure
^^^^^^^^^^^^^^^^^^^^^^^^^^
