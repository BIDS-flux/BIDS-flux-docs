.. _access-to-data:

Access to Data
==============

Each site will host the data collected locally, howerver the collective pooled data will be available from the CPIP Green server, ask your local Data Manager how to best access data.

Ethics
------

TODO: fill information on ethics.

Downloading the dataset from the Green server
-----------------------

`DataLad <https://www.datalad.org/>`_ is a tool for versioning a large data structure in a git repository. The dataset can be explored without downloading the data, and it is easy to only download the subset of the data you need for your project. See the `DataLad handbook <http://handbook.datalad.org/en/latest/>`_ for further information.

We recommend creating an SSH key (if not already present) on the machine on which the dataset will be installed and adding it to Git platform. See the official `GitHub instructions <https://help.github.com/en/enterprise/2.15/user/articles/adding-a-new-ssh-key-to-your-github-account>`_ on how to create and add a key to your account.

To obtain the data, you need to install a recent version of the `DataLad software <http://handbook.datalad.org/en/latest/intro/installation.html>`_, available for Linux, macOS, and Windows. Note that you need to have valid login credentials to access the NeuroMod git as well as the NeuroMod `Amazon S3 <https://aws.amazon.com/s3>`_ fileserver. Once you have obtained these credentials, you can proceed as follows in a terminal:

.. code-block:: bash

   # Install recursively the dataset and subdataset of the current project.
   # If using SSH git clone as follows, you can set your public SSH key in the present git to ease future updates.
   datalad install -r git@git.cpipstudy.org:CPIP-GREEN/bids.git
   # If errors show up relative to .heudiconv subdataset/submodule, this is OK, they are not published (will be cleaned up in the future).
   cd bids

Versioning
----------

By default, this will install the latest stable release of the dataset, which is the recommended version to get for a new analysis. If you need to work on a specific version (for instance, to reproduce a result), you can change to the appropriate tag with:

.. code-block:: bash

   git checkout 2025

We now set an environment variable for the credentials to the file server. The S3 `access_key` and `secret_key` will be provided by the data manager after being granted access to cpip by the user access committee.

.. code-block:: bash

   # This needs to be set in your `bash` every time you want to download data.
   export AWS_ACCESS_KEY_ID=<s3_access_key> AWS_SECRET_ACCESS_KEY=<s3_secret_key>

Preprocessed data
-----------------

For analysis of fMRI data, it is preferable to directly get the preprocessed data from the BIDS derivatives (smriprep and fmriprep for now).

.. code-block:: bash

   datalad install git@git.cpipstudy.org:CPIP/derivatives.git
   cd derivatives

You can install the sub-datasets you are interested in (instead of installing all of them) using, for instance:

.. code-block:: bash

   datalad get -n smriprep fmriprep

and then get only the files you need (for instance, MNI space output):

.. code-block:: bash

   datalad get smriprep/sub-*/anat/*space-MNI152NLin2009cAsym_*
   # get all anatomical output in MNI space
   datalad get fmriprep/movie10/sub-*/ses-*/func/*space-MNI152NLin2009cAsym_*
   # get all functional output in MNI space

You can add the flag ``-J n`` to download files in parallel, with ``n`` being the number of threads to use.

The source data used for preprocessing (including raw data) are referenced as sources in the preprocessed dataset following `Yoda <https://handbook.datalad.org/en/latest/basics/101-127-yoda.html>`_, so as to track provenance. You can also track the version of the cneuromod dataset you are using by installing it in a DataLad dataset created for your project.

Stimuli and event files
-----------------------

You will likely need the event files and stimuli for your analysis, which can be obtained from the sourcedata reference sub-datasets, for example:

.. code-block:: bash

   datalad get -r fmriprep/movie10/sourcedata/movie10/stimuli fmriprep/movie10/sourcedata/movie10/*_events.tsv

or to get subject-specific event files for tasks collecting behavioral responses:

.. code-block:: bash

   datalad get -r fmriprep/movie10/sourcedata/bids/sub-*/ses-*/func/*_events.tsv

Updates
-------

The dataset will be updated with new releases, so you might want to get these changes (unless you are currently running analyses or trying to reproduce results). The main branches of all datasets will always track the latest stable release.

.. code-block:: bash

   # update the dataset recursively
   datalad update -r --merge --reobtain-data

Once your local dataset clone is updated, you might need to pull new data, as some files could have been added or modified. The ``--reobtain-data`` flag should automatically pull files that you had already downloaded in case these were modified.

