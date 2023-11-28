Calgary Servers Configuration
=============================

.. .. figure:: ../../_static/infographics/Visio-C-PIP Deployment - Logical - v1.0.pdf
..    :name: fig-deployment-logical

.. figure:: ../../_static/infographics/cpip-diagram2.png
   :width: 600px

   Logical Deployment Diagram

In the figure above, you can see the logical deployment diagram proposed by the Calgary IT. The Montreal and Toronto sites may differ in many of these details, but the diagram pertaining to the two servers (the connectivity, user access, Compute Canada) should be very similar.

Server Configuration
--------------------

For Calgary, the development will be performed on two bare-metal servers running RHEL 8.x with no ZFS. The secure data server and the secure processing server:

#. **Server Model:**

   a. Secure data server: Dell PowerEdge R760XD2

   b. Secure processing server: Dell PowerEdge R7525

#. **ISO:** RedHat 8.x Calgary specific.

#. **Hardware Configuration:**

   #. **CPU and RAM Allocation:**

      a. Secure data server: 2x 4410Y 12 Cores, 16x 16G RAM (256 GB total)

      b. Secure processing server: 2x 7453 56 Cores 16x 32G RAM (512 GB total)

   #. **Storage:**

      a. Secure data server: 12x 16TB NLSAS

      b. 2x 800GB 3DWPD, 2x 3.2TB NVME 3DWPD

      c. Network Configuration: Can be better seen in the diagram.

      d. Disk Configuration: 
   
   #. **Software and Application Configuration:**

      a. RedHat 8.x was a requirement from the University of Calgary, which does not allow us to use ZFS.

      b. Required software includes docker, Git, Datalad, Git-annex, self-hosted gitlab, gitlab runner, self-hosted MinIO.

   #. **User Account and Permissions:** Will be linked to the University of Calgary's active directory.

   #. **Security Configuration:** Firewall configuration can be seen in the diagram.

