.. _storescp:

StoreSCP Installation and Setup
===============================

Calgary
+++++++

Docker Swarm Installation
-------------------------

#. Clone the unf `stack repository <https://gitlab.unf-montreal.ca/ni-dataops/stack.git>`_.

#. Move into the proper folder of the repository.

    .. code-block:: bash

        cd stack/storage_server

#. If you are using self signed certificates, switch into the selfsigned-certs branch and make sure that the storescp image was built including the selfsigned certificates.

#. Create the required secrets.

    .. code-block:: bash

        sudo docker secrets create name-of-secret secret-file
        # secret-file can be any text file containing the needed information.
        # OR
        echo "xxxxxxxxxx" | docker secret create name-of-secret -
        # make sure to remove the entry from the server's history

.. important:: 
   
   Make sure that the docker-compose file is pointing to those secrets for their use inside the container.

.. important::
   Make sure that the docker-compose file point the service deployment to the manager node using the constraints. 

      .. code:: yml

         deploy:
         placement:
               constraints:
               - node.hostname == manager-node.ca



#. Run the docker command 

    .. code-block:: bash

        docker stack deploy --compose-file docker-compose.dicom-rcv.yml cpip

    .. important:: 

        In docker swarm in order to mount a volume to a container, such volume must exist. This is not necessary using docker compose where directories are created if missing.

#. More documentation on how to automatically deploy the storescp enviromental varibles to come.

#. Debbugging

    .. note:: 

        Check `this <https://stackoverflow.com/questions/55087903/docker-logs-errors-of-services-of-stack-deploy>`_ post for debbugging.

    .. important:: 

        In docker swarm, in order to mount a volume to a container, such volume must exist. This is not necessary using docker compose where directories are created if missing.

Docker Compose Installation
---------------------------

StoreSCP stands for ``"Store Service Class Provider"``. In the DICOM network communication model, a Service Class Provider (SCP) is an entity that provides services to a Service Class User (SCU). In this case, ``storescp acts as a receiver (server)`` in a network exchange where it accepts DICOM images or data sent over the network from a sender (client), which is typically a SCU like a PACS system, MRI or CT scanner, or another workstation.

The C-PIP pipeline will have a StoreSCP container listening for DICOMS sessions being pushed from the MRI. StoreSCP deployment is simple since it relies on docker and all the configuration/code is already in a GitHub repository.

#. First, make sure you have :ref:`docker and docker compose <dockerinstall>` installed.

#. Then clone the GitHub repository `https://gitlab.com/cal_cpip/calgary-servers.git <https://gitlab.com/cal_cpip/calgary-servers.git>`_ which will contain the requied configurations, dockerfiles, and docker compose files.

   .. note:: 

      Some modifications have been made to this repository in order to function using ``self-signed certificates``.

#. In the sequoia folder of the repository you will find the docker compose file ``docker-compose_storescp_dev.yml``.

#. Check the following configuration files inside the ``calgary-servers/sequoia/storescp/`` folder:

   * storescp/exect_on_study_received.py
   * storescp/start.sh
   * storescp/unf_**.py
   * storescp/_vars.env

#. Finally, all you need to do is run the following command to spin up this container.

.. code-block:: bash

   sudo docker compose -f calgary-servers/sequoia/docker-compose_storescp_dev.yml up

