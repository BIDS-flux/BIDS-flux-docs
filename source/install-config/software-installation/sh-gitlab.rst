Self-hosted GitLab
=============================

Instalation Calgary
+++++++++++++++++++

.. .. figure:: ../../_static/infographics/Visio-C-PIP Deployment - Logical - v1.0.pdf
..    :name: fig-deployment-logical

.. .. figure:: ../../_static/infographics/cpip-diagram2.png
..    :width: 600px

   .. Logical Deployment Diagram

`Follow this installation guide for installing gitlab in centos/redhat 8, it also works for redhat 9. <https://about.gitlab.com/install/#centos-7>`_ It is imporant to make the following considerations when following the steps.

#. **Disable user creation to avoid undesired users** `follow these instructions. <https://computingforgeeks.com/disable-user-signup-on-gitlab-welcome-page/>`_

#. **Secure GitLab Server with self-signed certificates.**

   .. creationofssl:

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

         b. Copy the cerficate you created in :ref:`Create a self-signed certificate <creationofssl>` into the /etc/docker/daemon.json file, create if it does not exist.

         .. code-block:: bash

            sudo cp /etc/gitlab/ssl/cpip.ahs.ucalgary.ca.crt /etc/docker/cert.d/cpip.ahs.ucalgary.ca:5050/ca.crt

         c. Add the hostnames to the insecure registries json file in /etc/docker/daemon.json. I added both with and without port but I am almost positive you only need the cpip.ahs.ucalgary.ca:5050

         .. code-block:: json

            {
            "insecure-registries" : [ "cpip.ahs.ucalgary.ca","cpip.ahs.ucalgary.ca:5050" ]
            }

         d. You also need to make sure that your system trusts the created certificate by following `these instructions <https://docs.docker.com/registry/insecure/#use-self-signed-certificates>`_.

         .. code-block:: bash

            cp /etc/gitlab/ssl/cpip.ahs.ucalgary.ca.crt /etc/pki/ca-trust/source/anchors/cpip.ahs.ucalgary.ca.crt
            update-ca-trust

      
   #. **Installation of GitLab using docker.**
   
   The installation of pretty much everything is possible using Docker. All you need to do is follow their `installation guide <https://docs.gitlab.com/ee/install/docker.html#install-gitlab-using-docker-compose>`_ using docker compose. I was not able to make this work on Calgary's servers using RedHat.
