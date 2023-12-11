.. _gitlab-runner-setup:

GitLab Runners Setup
=============================

Calgary
+++++++

For Calgary we will use a docker compose file living in a repository to install GitLab runner. 

Either clone the repository: `https://gitlab.com/cal_cpip/calgary-servers.git <https://gitlab.com/cal_cpip/calgary-servers.git>`_ and run the following command:

.. code-block:: bash

   sudo docker compose -f calgary-servers/sequoia/docker-compose.gitlab-runner_dev.yml up

Or follow these outlined steps:

#. First create a folder with a Dockerfile like the following inside a folder you can call gitlab-runner.

   .. code-block:: bash

      mkdir gitlab-runner
      cd gitlab-runner

#. Create the Dockerfile and add the necessary certificates straight into the image.

   .. code-block:: dockerfile

      FROM gitlab/gitlab-runner:alpine

      RUN mkdir -p /etc/ssl/certs/
      RUN update-ca-certificates

      RUN apk add 

      COPY minio.ahs.ucalgary.ca.crt /etc/ssl/certs/cert1.crt
      COPY cpip.ahs.ucalgary.ca.crt /etc/ssl/certs/cert2.crt

      RUN cat minio.ahs.ucalgary.ca.crt >> /etc/gitlab-runner/certs/ca.crt
      RUN cat cpip.ahs.ucalgary.ca.crt >> /etc/gitlab-runner/certs/ca.crt

      RUN update-ca-certificates


#. Then create a docker-compose.yml file with the following contents.

   .. code-block:: yaml

      version: "3.6"
      services:
      gitlab-runner:
         build:
            context: ./gitlab-runner/
         ports:
            - "8093:8093"
         volumes:
            - ./gitlab-runner/config:/etc/gitlab-runner/
            - /var/run/docker.sock:/var/run/docker.sock

#. Run this command to spin up the gitlab-runner container.

   .. code-block:: bash

      sudo docker compose -f docker-compose.yml up

#. Follow `this documentation <https://docs.gitlab.com/runner/configuration/tls-self-signed.html>`_ to make sure that your gitlab runner can trust your self signed certificate.

#. To create this runners, you will need to first go into your gitlab instance interface **as an admin**. Navigate to the ``admin area navigate into CI/CD>runners>new instance runner`` and follow the steps util you get the token required to register your runner.   

#. Now, on the server where you installed gitlab-runner, if you are using docker, you will need to create your gitlab-runners using something like the following:

   .. code-block:: bash

      docker exec -it <your-gitlab-container> gitlab-runner register -n -u <your-gitlab-instance, for instance: https://cpip.ahs.ucalgary.ca> --token glrt-amxjdeXmzWMyHYSsbRBh --executor docker --description bids-runner --docker-privileged=false --docker-volumes "/certs/client" "/mnt/data/mri/ria-dicoms:/data/ria-dicoms:ro" "/var/run/docker.sock:/var/run/docker.sock" "/mnt/data/mri:/data/" --docker-image "docker:20.10.16"

   .. important::

      For this previous command to work you will need to use the token obtained in the previous step which will start with ``glrt``.

   .. note::

      If you did not use docker to install gitlab-runner, you should remove: ``docker exec -it <your-gitlab-container>``.

   .. note::

      ``"/mnt/data/mri/ria-dicoms:/data/ria-dicoms:ro"`` and ``"/mnt/data/mri:/data/"`` are mounting the mri data and ria-dicoms archive from the system where the :ref:`StoreSCP <storescp>` container is saving the dicom sessions.

#. At least 3 different runners need to be created as instance-wide runners.

   a. Untagged jobs
   
   b. Bids conversion; tag = bids

   c. For pre-processing; tag = preproc

#. Your new gitlab runner's configuration should have been added to the /etc/gitlab-runner/config.toml from which we will need to follow this `documentation <https://docs.gitlab.com/ee/administration/packages/container_registry.html#using-self-signed-certificates-with-container-registry>`_ in order to make sure that the self signed certificates are included to the docker in docker. Basically, you are need to make sure your runner's configuration contains ``privileged = false`` and the volume ``/var/run/docker.sock:/var/run/docker.sock`` to mount the docker deamon into the docker.

   .. code-block:: toml
      
      [[runners]]
         name = "bids-runner-instance"
         url = "https://cpip.ahs.ucalgary.ca"
         id = 8
         token = "glrt-amxjdeXmzWMyHYSsbRBh"
         token_obtained_at = 2023-11-01T18:45:14Z
         token_expires_at = 0001-01-01T00:00:00Z
         executor = "docker"
         [runners.docker]
            tls_verify = false
            image = "docker:20.10.16"
            privileged = false
            disable_entrypoint_overwrite = false
            oom_kill_disable = false
            disable_cache = false
            volumes = ["/certs/client", "/cache", "/mnt/data/mri:/data/", "/mnt/data/mri:/data/", "/mnt/data/mri/ria-dicoms:/data/ria-dicoms:ro", "/var/run/docker.sock:/var/run/docker.sock"]
            shm_size = 0
            network_mtu = 0

#. Common errors/solutions when dealing with SSL could be found `here. <https://docs.gitlab.com/omnibus/settings/ssl/ssl_troubleshooting.html>`_