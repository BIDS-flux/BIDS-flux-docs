Self-hosted GitLab Installation and Setup
===============================

Montreal
+++++++++++++++++++

Installation
------------

.. _creationofssl:

#. **Install** `self-hosted Gitlab <https://about.gitlab.com/install/#ubuntu>`_ on the server acting as manager node for the docker swarm (server-1).

#. **Setup** `self-signed certificates <https://docs.gitlab.com/omnibus/settings/ssl/index.html#configure-https-manually>`_ to be copied into the secrets directory (see below) on both servers.

#. **Disable user creation to avoid undesired users** `follow these instructions. <https://computingforgeeks.com/disable-user-signup-on-gitlab-welcome-page/>`_

#. Talk to whoever manages your network to have them add your new hostname (e.g., cpip.server-2.imagerie.user-vms.cqgc.hsj.rtss.qc.ca) to the DNS.

#. Follow these `instructions 1 <https://docs.gitlab.com/omnibus/settings/ssl/index.html>`_ or `instructions 2 <https://computingforgeeks.com/how-to-secure-gitlab-server-with-ssl-certificate/?expand_article=1>`_ and reconfigure gitlab to accept self-signed certificates.
   #. Note: use `this information to create the keys <openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout 10.128.81.225.key -out 10.128.81.225.crt>`_ where here we are using an IP, but ideally we would be using a DNS associated to that IP.

#. **Enable a container registry with the same self-signed certificate.**

.. _docker_swarm_gitlab:

Docker Swarm GitLab Installation
--------------------------------

#. Follow the steps for the the creation of selfsigned certificates that was previously :ref:`outlined <creationofssl>`. Or not, if you already have certificates for the required hostnames.

#. For Montreal's setup we will deploy GitLab, StoreSCP in the manager node (server-1), and the gitlab-runners in a worker node (data/processing server-2).

#. Create a ``docker swarm manager node`` to deploy GitLab, StoreSCP, and connect MinIO to the UniC object store.

   .. code:: bash

      sudo docker swarm init --data-path-port 9789 --advertise-addr 127.0.0.1


   .. warning::
      
      Be aware of the issues with docker swarm in a `VMWare virutal machine <https://portal.portainer.io/knowledge/known-issues-with-vmware>`_.

#. SSH into the worker node (processing server-2) and run the following command with the information obtained from the previous command.

   .. code:: bash

      
      sudo docker swarm join --token TOKEN server-1.internal.imagerie.user-vms.cqgc.hsj.rtss.qc.ca:2377
   
   You can then verify the status of the swarm on the manager node running:

   .. code:: bash

      sudo docker ps

   .. warning::
      
      You must use the hostname for server-1 on VLAN4 here identified by the "internal" keyword.

#. Create an attachable docker overlay network. The subnet/gateway was defined to avoid potential issues with the port ranges used by the University of Calgary.

   .. code:: bash

      docker network create --driver=overlay --attachable cpip-network --subnet=192.11.0.0/16 --gateway=192.11.0.2

   You can list the docker networks and get more specific status information on the cpip-network using:

   .. code:: bash
      
      sudo docker network ls
      sudo docker network inspect cpip-network

#. Clone the UNF repository `ni-dataops/stack <https://gitlab.unf-montreal.ca/ni-dataops/stack.git>`_.

   .. note:: 

      If you are using ``self-signed certificates``, you might use the selfsigned-cert branch, for this branch custom docker images will need to be created before stack deployment. Update: use montreal branch.

#. Create the necessary docker secrets.

   Under ``deploy`` there is a script called ``create_directory.sh`` and ``generate_secrets.sh``. Run the directory creation          script, and then generate the secrets. Make sure that you have a folder under ``~/ni-dataops/stack/secrets`` where your            secrets are located in raw text form i.e. ``gitlab_root_password``.

   Make sure that the ``generate_secrets.sh`` script generates all the required secrets for each service, as can be seen in the docker compose config yaml file:

   .. code:: bash

      secrets:
        gitlab_root_password:
          file: ./secrets/gitlab_root
        gitlab_token_local:
          file: ./secrets/gitlab_local
        gitlab_token_remote:
          file: ./secrets/gitlab_remote
        cert:
          file: ./secrets/bundle.crt
        key:
          file: ./secrets/cert.key
        minio_pass:
          file: ./secrets/minio_pass
        minio_conf:
          file: ./secrets/mc.conf
        dicom_bot_token:
          file: ./secrets/dicom_token
        s3_id:
          file: ./secrets/s3_id
        s3_key:
          file: ./secrets/s3_key
        ssh_passphrase:
          file: ./secrets/passphrase

#. Make sure that the docker-compose file point the service deployment to the manager node using the constraints and attached to the right network. 

    .. code:: yml

        deploy:
        placement:
            constraints:
            - node.hostname == manager-node.ca            
      
    .. code:: yml
      
         networks:
            - cpip_network
      networks:
      cpip_network:
         external: true

#. Do the modifications necesary to set your `hostname` and run the command:

   .. code:: 

      sudo GITLAB_HOME=/srv/gitlab/ docker stack deploy -c docker_compose.gitlab.yml cpip

   .. important:: 

      In docker swarm, in order to mount a volume to a container, such volume must exist. This is not necessary using docker compose where directories are created if missing.

   .. note:: 

      You can find information on how to change password using the terminal in `this disscusion <https://stackoverflow.com/questions/55747402/docker-gitlab-change-forgotten-root-password>`_.

         .. code:: ruby

            #You will need to do this through the ruby console
            user = User.where(id: 1).first
            user.password = 'your secret'
            user.password_confirmation = 'your secret'
            user.state = 'active'
            user.save!
            exit

#. More documentation on how to automatically set the instance wide CI/CD gitlab variables to come.

#. There will be a way to standardize/automatically set the instance wide CI/CD gitlab variables  using python scripts and json configuration files from the `ni-dataops/stack/gitlab_server/config <https://gitlab.unf-montreal.ca/ni-dataops/stack/-/tree/main/gitlab_server/config?ref_type=heads>`_ UNF repository.

   .. code:: 

      #This way of creating ci-variables will involve running something like this

      python3 create_gitlab_variable.py ci-variable.json


#. Follow the previous steps to :ref:`configure gitlab <gitlab_config>`.





Calgary
+++++++

.. _docker_swarm_gitlab:

Docker Swarm GitLab Installation
--------------------------------

#. Follow the steps for the the creation of selfsigned certificates that was previously :ref:`outlined <creationofssl>`. Or not, if you already have certificates for the required hostnames.

#. For Calgary's setup we will deploy GitLab, StoreSCP, and MinIO in the manager node, and the gitlab-runners in a worker node (data server).

#. Create a ``docker swarm manager node`` to deploy GitLab, StoreSCP, and MinIO.

   .. code:: bash

      docker swarm init --dport 9789

   .. warning::
      
      Be aware of the issues with docker swarm in a `VMWare virutal machine <https://portal.portainer.io/knowledge/known-issues-with-vmware>`_.

#. SSH into the worker node (processing server) and run the following command with the information obtained from the previous command.

   .. code:: bash

      docker swarm join --token TOKEN --advertise-addr <IP-ADDRESS-OF-WORKER-1> <IP-ADDRESS-OF-MANAGER>:2377

#. Create an attachable docker overlay network. The subnet/gateway was defined to avoid potential issues with the port ranges used by the University of Calgary.

   .. code:: bash

      docker network create --driver=overlay --attachable cpip-network --subnet=192.11.0.0/16 --gateway=192.11.0.2


#. Clone the UNF repository `ni-dataops/stack <https://gitlab.unf-montreal.ca/ni-dataops/stack.git>`_.

   .. note:: 

      If you are using ``self-signed certificates``, you might use the selfsigned-cert branch, for this branch custom docker images will need to be created before stack deployment.

#. Create the necesary docker secrets.

    .. code-block:: bash

        sudo docker secrets create name-of-secret secret-file
        # secret-file can be any text file containing the needed information.
        # OR
        echo "xxxxxxxxxx" | docker secret create name-of-secret -
        # make sure to remove the entry from the server's history

#. Make sure that the docker-compose file point the service deployment to the manager node using the constraints and attached to the right network. 

    .. code:: yml

        deploy:
        placement:
            constraints:
            - node.hostname == manager-node.ca            
      
    .. code:: yml
      
         networks:
            - cpip_network
      networks:
      cpip_network:
         external: true

#. Do the modifications necesary to set your `hostname` and run the command:

   .. code:: 

      sudo GITLAB_HOME=/srv/gitlab/ docker stack deploy -c docker_compose.gitlab.yml cpip

   .. important:: 

      In docker swarm, in order to mount a volume to a container, such volume must exist. This is not necessary using docker compose where directories are created if missing.

   .. note:: 

      You can find information on how to change password using the terminal in `this disscusion <https://stackoverflow.com/questions/55747402/docker-gitlab-change-forgotten-root-password>`_.

         .. code:: ruby

            #You will need to do this through the ruby console
            user = User.where(id: 1).first
            user.password = 'your secret'
            user.password_confirmation = 'your secret'
            user.state = 'active'
            user.save!
            exit

#. More documentation on how to automatically set the instance wide CI/CD gitlab variables to come.

#. There will be a way to standardize/automatically set the instance wide CI/CD gitlab variables  using python scripts and json configuration files from the `ni-dataops/stack/gitlab_server/config <https://gitlab.unf-montreal.ca/ni-dataops/stack/-/tree/main/gitlab_server/config?ref_type=heads>`_ UNF repository.

   .. code:: 

      #This way of creating ci-variables will involve running something like this

      python3 create_gitlab_variable.py ci-variable.json


#. Follow the previous steps to :ref:`configure gitlab <gitlab_config>`.

Debbugging
^^^^^^^^^^

#. Allow a new ssh port in the system can be achieved. Follow `this post <https://stackoverflow.com/questions/11672525/centos-6-3-ssh-bind-to-port-xxx-on-0-0-0-0-failed-permission-denied>`_ for more information.
#. There is an error when using docker swarm for the deployment `this post <https://www.awaimai.com/en/3100.html>`_ mentions how to solve it.

   .. code:: yaml

      # All you need to do is add the following configurtion to the gitlab runners config in /etc/gitlab-runner/config.toml
      [[runners]]
      #....
      [runners.docker]
         pull_policy = ["if-not-present", "always"]
         #...

Direct GitLab Installation
--------------------------

We follow this `installation guide <https://about.gitlab.com/install/#centos-7>`_ for installing gitlab in centos/redhat 8, it also works for redhat 9. It is imporant to make the following considerations when following the steps.

.. _creationofssl:

#. **Disable user creation to avoid undesired users** `follow these instructions. <https://computingforgeeks.com/disable-user-signup-on-gitlab-welcome-page/>`_

#. **Secure GitLab Server with self-signed certificates.**

   #. Create a self-signed certificate. `Click here for the creation of a self signed SSL certificate on centos or redhat. <https://jfrog.com/help/r/general-what-should-i-do-if-i-get-an-x509-certificate-relies-on-legacy-common-name-field-error/a-new-valid-certificate-needs-to-be-created-to-include-the-subjectaltname-property-and-should-be-added-directly-when-creating-an-ssl-self-signed-certificate-using-openssl-command-by-specifying-an-addext-flag.-for-instance>`_ 

      .. note::
         This link also contains information on how to eliminate the problem: x509: certificate relies on legacy Common Name field, use SANs instead. This will help you create a new certificate that will contain a subject alteranative name.

      For instance for an self-signed certificate cpip.ahs.ucalgary.ca you would do the following.

      .. code-block:: bash

         openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/gitlab/ssl/cpip.ahs.ucalgary.ca.key -addext "subjectAltName = DNS:cpip.ahs.ucalgary.ca" -out /etc/ gitlab/ssl/cpip.ahs.ucalgary.ca.crt


   #. Talk to whoever manages your network to have them add your new hostname (e.g., cpip.ahs.ucalgary.ca) to the DNS. Wheter or not this is important will depend on who will need to have access to gitlab's interface.

   #. Follow these `instructions 1 <https://docs.gitlab.com/omnibus/settings/ssl/index.html>`_ or `instructions 2 <https://computingforgeeks.com/how-to-secure-gitlab-server-with-ssl-certificate/?expand_article=1>`_ and reconfigure gitlab to accept self-signed certificates.

#. **Enable a container registry with the same self-signed certificate.**

   #. You can use the same certificate which means that your registry will be deployed on the same domain name but with a different port. For instance: cpip.ahs.ucalgary.ca:5050.

   #. To do this you need to follow these `instructions <https://docs.gitlab.com/ee/administration/packages/container_registry.html?tab=Linux+package+%28Omnibus%29#configure-container-registry-under-an-existing-gitlab-domain>`_ to configure the container registry under an existing gitlab domain.

   #. `Follow the steps on this link <https://docs.gitlab.com/omnibus/settings/ssl/index.html#install-custom-public-certificates>`_ to install self-signed certificates and make sure they are trusted by adding the public part of the PEM .crt certificate to the /etc/gitlab/trusted-certs/

      a. This is how you can get the PEM public certificate.

         .. code-block:: bash

            sudo openssl x509 -inform PEM -in /etc/gitlab/ssl/cpip.ahs.ucalgary.ca.crt -pubkey -noout > /etc/gitlab/trusted-certs/cpip.ahs.ucalgary.ca.crt

      b. You need to make sure that you also add the certificate to docker daemon and to the system-wide trusted certifictes folders like so:

         a. First to docker: follow the steps suggested in `this post <https://forum.gitlab.com/t/cannot-login-docker-with-self-signed-certificate/81488>`_.

            a. Copy the cerficate you created in :ref:`Create a self-signed certificate <creationofssl>` into the /etc/docker/cert.d folder, create if it does not exist.

               .. code-block:: bash

                  sudo cp /etc/gitlab/ssl/cpip.ahs.ucalgary.ca.crt /etc/docker/cert.d/cpip.ahs.ucalgary.ca:5050/ca.crt

            b. Add the hostnames to the insecure registries json file in /etc/docker/daemon.json. I added both with and without port but I am almost positive you only need the cpip.ahs.ucalgary.ca:5050

               .. code-block:: json

                  {
                  "insecure-registries" : [ "cpip.ahs.ucalgary.ca","cpip.ahs.ucalgary.ca:5050" ]
                  }

         b. You also need to make sure that your system trusts the created certificate by following `these instructions <https://stackoverflow.com/questions/22509271/import-self-signed-certificate-in-redhat>`_. These are specific o RedHat 8 follow a simillar guide for your OS.

            .. code-block:: bash

               sudo cp /etc/gitlab/ssl/cpip.ahs.ucalgary.ca.crt /etc/pki/ca-trust/source/anchors/cpip.ahs.ucalgary.ca.crt
               sudo update-ca-trust extract

      .. note:: 

         You can find information on how to change password using the terminal in `this disscusion <https://stackoverflow.com/questions/55747402/docker-gitlab-change-forgotten-root-password>`_.

            .. code:: ruby

               #You will need to do this through the ruby console
               user = User.where(id: 1).first
               user.password = 'your secret'
               user.password_confirmation = 'your secret'
               user.state = 'active'
               user.save!
               exit

.. _gitlab_config:

Configuration
-------------

After installation, there are additional configurations required before the pipeline is ready to process images.

#. First, install :ref:`gitlab-runner <gitlab-runner-setup>` following the tutorials, and create the minimal number of instance-wide (can be accessed by jobs triggered from any repository, even if created after the creation of the runners) runners required.

#. Create an empty new project called ni-dataops.

#. Clone the `ni-dataops ci-pipelines and containers repositories from https://gitlab.unf-montreal.ca/ni-dataops <https://gitlab.unf-montreal.ca/ni-dataops>`_ and push upstream to you self-hosted gitlab. Access (token-access) to this repository should be allowed from other repositories, this will permit newly created repositories containing data to access the processing pipelines.

   .. note:: 

      This can be done in the CI/CD settings of the gitlab project in the interface.

   .. code-block:: bash

      git clone https://gitlab.com/cal_cpip/ni-dataops.git
      cd ni-dataops
      git remote add <name-of-remote> <url-of-self-hosted-gitlab-project, for instance https://cpip.ahs.ucalgary.ca/ni-dataops.git>
      git push -u <name-of-remote> main

   .. note::

      Check branch permissions to make sure you can push up to it.

#. Create some users which will be necessary to run some of the task like DICOM to BIDS conversion, processing, etc.

   a. bids_bot = Admin level so it can access all repos
   b. dicom_bot = Admin level because its token need to have elevated privileges to use with the GitLab API.

#. ``Install MinIO`` in you data server following :ref:`this guide <minio>`.

#. Some instance-wide variables need to be setup in order for CI/CD pipelines to use then even when new repositores are added after.

   .. note:: 

      To do this you need login into the self-hosted GitLab's admin area. There, you will need to navigate to the settings > CI/CD > Variables.
   
   a. BIDS_API_TOKEN = access token for the bids_bot

   b. BOT_SSH_KEY = this key is generated from the gitlab-runner from the ``bids runner``

      .. note:: 

         This is the private key starting with -------something------- and ending with -----------end------------. It should be generated from inside the runner instance.

      .. note:: 

         Additionally, the public part of the key added need to be added to bids_bot profile ssh_keys.

   c. GIT_BOT_USERNAME = bids_bot

   d. GIT_BOT_EMAIL = bids_bot@ahs.ucalgary.ca

   e. S3_SECRET = S3 password set in the :ref:`minio installation <minio>`

   f. SSH_KNOWN_HOSTS = created copying the output of ssh-keyscan <IP of your self-hosted gitlab> into the value of the variable.

      .. note:: 

         This variable needs to contain Host and IP of the self-hosted Gitlab



Debbugging
----------

#. Allow a new ssh port in the system can be achieved. Follow `this post <https://stackoverflow.com/questions/11672525/centos-6-3-ssh-bind-to-port-xxx-on-0-0-0-0-failed-permission-denied>`_ for more information.
#. There is an error when using docker swarm for the deployment `this post <https://www.awaimai.com/en/3100.html>`_ mentions how to solve it.

   .. code:: yaml

      # All you need to do is add the following configurtion to the gitlab runners config in /etc/gitlab-runner/config.toml
      [[runners]]
      #....
      [runners.docker]
         pull_policy = ["if-not-present", "always"]
         #...
