.. _dockerinstall:

Docker Installation
=============================

Montreal
+++++++

# Docker Installation

* Montreal is working with Ubuntu. `Installation of docker <https://docs.docker.com/engine/install/ubuntu/>`_
* `Installation of docker compose <https://docs.docker.com/compose/install/linux/>`_

# Docker Registry Setup

## Step 1: Verify the Image is Pushed to the Registry
Tag the Image for the Registry:


Copy code
sudo docker tag scratch-for-setup:latest server-1.imagerie.user-vms.cqgc.hsj.rtss.qc.ca:5000/scratch-for-setup:latest
Push the Image to the Registry:

sh
Copy code
sudo docker push server-1.imagerie.user-vms.cqgc.hsj.rtss.qc.ca:5000/scratch-for-setup:latest
Verify the Image in the Registry:
List the repositories in your registry to ensure the image is there:

sh
Copy code
curl http://server-1.imagerie.user-vms.cqgc.hsj.rtss.qc.ca:5000/v2/_catalog
Step 2: Configure Docker to Access the Registry
If the registry requires authentication:

Log in to the Registry:
Use Docker to log in to your registry:

sh
Copy code
sudo docker login server-1.imagerie.user-vms.cqgc.hsj.rtss.qc.ca:5000
Provide your username and password when prompted.

Pull the Image from the Registry:
Pull the image to verify that it is accessible:

sh
Copy code
sudo docker pull server-1.imagerie.user-vms.cqgc.hsj.rtss.qc.ca:5000/scratch-for-setup:latest
Example Commands and Expected Outputs
Tag the Image for the Registry:

sh
Copy code
sudo docker tag scratch-for-setup:latest server-1.imagerie.user-vms.cqgc.hsj.rtss.qc.ca:5000/scratch-for-setup:latest
Push the Image to the Registry:

sh
Copy code
sudo docker push server-1.imagerie.user-vms.cqgc.hsj.rtss.qc.ca:5000/scratch-for-setup:latest
Expected output should show the layers being pushed successfully.

Verify the Image in the Registry:

sh
Copy code
curl http://server-1.imagerie.user-vms.cqgc.hsj.rtss.qc.ca:5000/v2/_catalog
Expected output:

json
Copy code
{"repositories":["scratch-for-setup"]}
Log in to the Registry:

sh
Copy code
sudo docker login server-1.imagerie.user-vms.cqgc.hsj.rtss.qc.ca:5000
Provide credentials when prompted.

#. Pull the Image from the Registry:

  
sudo docker pull server-1.imagerie.user-vms.cqgc.hsj.rtss.qc.ca:5000/scratch-for-setup:latest
Expected output should show the layers being pulled successfully.



Calgary
+++++++

* Calgary is working with RedHat. Docker does not have direct packages for installation of RedHat8 with x86_64 arquitecture, thus, we will use the `CentOS installation packages. <https://docs.docker.com/engine/install/centos/>`_
* Make sure to also `install docker compose <https://docs.docker.com/compose/install/linux/>`_ since it will be used to install for instance :ref:`StoreSCP. <storescp>`
