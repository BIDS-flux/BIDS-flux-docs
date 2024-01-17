.. _minio:

MinIO Installation
=============================

Calgary
+++++++

You can find the installation guides for the different operating systems in this `documentation <https://min.io/docs/minio/linux/operations/install-deploy-manage/deploy-minio-single-node-single-drive.html#minio-snsd>`_.

#. Calgary is working with RedHat8, therefore, we will use the following `installation <https://min.io/docs/minio/linux/operations/install-deploy-manage/deploy-minio-single-node-single-drive.html#minio-snsd>`_ package:

    .. code-block:: bash

        wget https://dl.min.io/server/minio/release/linux-amd64/archive/minio-20231016041343.0.0.x86_64.rpm -O minio.rpm
        sudo dnf install minio.rpm

    Other considerations required include the follwoing:

    #. Create the Systemd Sevice File (/usr/lib/systemd/system/minio.service) followig `this steps <https://min.io/docs/minio/linux/operations/install-deploy-manage/deploy-minio-single-node-single-drive.html#minio-snsd>`_. 

        .. code-block:: text

            [Unit]
            Description=MinIO
            Documentation=https://min.io/docs/minio/linux/index.html
            Wants=network-online.target
            After=network-online.target
            AssertFileIsExecutable=/usr/local/bin/minio

            [Service]
            WorkingDirectory=/usr/local

            User=minio-user
            Group=minio-user
            ProtectProc=invisible

            EnvironmentFile=-/etc/default/minio
            ExecStartPre=/bin/bash -c "if [ -z \"${MINIO_VOLUMES}\" ]; then echo \"Variable MINIO_VOLUMES not set in /etc/default/minio\"; exit 1; fi"
            ExecStart=/usr/local/bin/minio server $MINIO_OPTS $MINIO_VOLUMES

            # MinIO RELEASE.2023-05-04T21-44-30Z adds support for Type=notify (https://www.freedesktop.org/software/systemd/man/systemd.service.html#Type=)
            # This may improve systemctl setups where other services use `After=minio.server`
            # Uncomment the line to enable the functionality
            # Type=notify

            # Let systemd restart this service always
            Restart=always

            # Specifies the maximum file descriptor number that can be opened by this process
            LimitNOFILE=65536

            # Specifies the maximum number of threads this process can create
            TasksMax=infinity

            # Disable timeout logic and wait until process is stopped
            TimeoutStopSec=infinity
            SendSIGKILL=no

            [Install]
            WantedBy=multi-user.target

            # Built for ${project.name}-${project.version} (${project.name})

    #. You need to change this according to the user/group that you are working under, or create a new user/group. There can only exist this /usr/lib/systemd/system/minio.service to avoid problems with the service.

        .. code-block:: bash

            User=minio-user # user that will be setup to have access to the minio
            Group=minio-user # gropu that will be setup to have access to the minio

    #. Make sure that you create the MinIO folder that is set up in /usr/lib/systemd/system/minio/minio.service to be your "mounted drive". I set ~/mnt/data so I do the following.

        .. code-block:: bash

            sudo mkdir /mnt/data

    #. You can create the user using the following commands.

        .. code-block:: bash

            groupadd -r minio-user
            useradd -M -r -g minio-user minio-user
            chown minio-user:minio-user /mnt/data #mounted drives set up in /usr/lib/systemd/system/minio/minio.service file, could be multiple

#. Create the environmnet variable file.

    If you are planning on using self signed certificates with a domain name for the S3-API, create a tls certificate with the appropriate ips/domains. Follow `these instructions <https://min.io/docs/minio/linux/operations/network-encryption.html>`_. You can use the `certgen <https://github.com/minio/certgen>`_ tool from the minio team.

    #. Download the certgen tool. 

        .. code-block:: bash

            #download the tool
            wget https://github.com/minio/certgen/releases/latest/download/certgen-linux-amd64
            #move it to /user/local/bin/
            sudo mv certgen-linux-amd64 /usr/local/bin/certgen
            #make it executable
            sudo chmod +x /usr/local/bin/certgen

    #. Create the certificates and place the TLS certificates for the domain (e.g. minio.ahs.ucalgary.ca) in the /certs directory, with the private key as private.key and public certificate as public.crt.

        .. code-block:: bash

            #for approx 10 years
            certgen -duration 220000h0m0s -host "139.48.221.19:9000,minio.ahs.ucalgary.ca" -
            #move them to the certs folder
            mv private.key ~/.minio/certs/
            mv public.crt ~/.minio/certs/
            #COPY INTO THE CERTS/CAs/ FOLDER BECAUSE WE ARE GOING FOR SELF SIGNED CERTIFICATES
            cp ~/.minio/certs/private.key ~/.minio/certs/CAs/myCA.crt

    #. After creating the certificates, create an environment variable file at /etc/default/minio.

        .. code-block:: bash

            MINIO_ROOT_USER=cpip-minio #root user used to login
            MINIO_ROOT_PASSWORD=cpip-minio-has-access #password used to login for root user
            # MINIO_VOLUMES sets the storage volume or path to use for the MinIO server.
            MINIO_VOLUMES="/mnt/data"
            # MINIO_SERVER_URL sets the hostname of the local machine for use with the MinIO Server
            # MinIO assumes your network control plane can correctly resolve this hostname to the local machine
            # Uncomment the following line and replace the value with the correct hostname for the local machine and port for the MinIO server (9000 by default).
            MINIO_SERVER_URL="https://minio.ahs.ucalgary.ca:9000"

#. Start the MinIO Server.

    #. Run the following commands to start the MinIO server.

        .. code-block:: bash

            sudo systemctl start minio.service
            sudo systemctl status minio.service
            journalctl -f -u minio.service
            sudo systemctl enable minio.service

    #. Install the mc (minio client binary) following `these instructions <https://min.io/docs/minio/linux/reference/minio-mc.html#mc-install>`_. Make sure to add the path to the binary to the ~/.bashrc file or copy the binary to the bin folder like we did for the certgen tool.

    #. Done. You can either access the minio console using the ip shown when you run journalctl -f -u minio.service or use ce MinIO client in order create an alias. This alias will allow you to perform admin tasks directly from the tool.

        .. code-block:: bash

            # this line will create an alias (cpip-minio-calgary) for our MinIO instance which will be used to manage it
            mc alias set cpip-minio-calgary https://minio.ahs.ucalgary.ca:9000 cpip-minio cpip-minio-has-access

    #. Creation and managing of users.

        There are different ways to create and manage users, for more information checkout the `mc admin tool <https://min.io/docs/minio/linux/reference/minio-mc-admin>`_.

Option 2: Docker swarm installation
-----------------------------------
 
#. Clone the unf `stack repository <https://gitlab.unf-montreal.ca/ni-dataops/stack.git>`_.

#. Move into the proper folder of the repository.

    .. code-block:: bash

        cd stack/storage_server

#. Calgary installation requires the creation of self-signed certificates using the certgen tool previously described.

#. Make sure that the docker.compose file is pointing to those secrets for their use inside the container.

#. Create the other secrets required.

    .. code-block:: bash

        sudo docker secrets create name-of-secret secret-file
        # secret-file can be any text file containing the needed information.

#. Run the docker command

    .. code-block:: bash

        docker stack deploy --compose-file docker-compose.minio.yml gitlab

#. Debbugging

    .. note:: 

        Check `this <https://stackoverflow.com/questions/55087903/docker-logs-errors-of-services-of-stack-deploy>`_ post for debbugging.

    .. note:: 

        In docker swarm in order to mount a volume to a container, such volume must exist. This is not necessary using docker compose where directories are created if missing.