Usage Notes
-----------

After completing the :ref:`software deployment <hardware-requirements>` you should have at least 2 servers/VMs (it could tecnically be just 1) a **data server** and a **processing server**. This section is intended to provide a guide on how to use the infraestructure for it's intended purpose of neuroimaging data management and analysis acceleration.

Data Flow
^^^^^^^^^
This section describes an overview of the data flow from the moment a study participant is scanned to the moment the data is available for a release. 

.. _diagram::

.. mermaid::

   %%{ init:
           { "theme": "forest",
           "sequence": { "showSequenceNumbers": true } }
        }%%
   sequenceDiagram
   box Gray Dicom Acquisition
   participant MRI Scanner
   participant Mercure as Mercure<br/>Storescp
   end
   box Orange Local Gitlab
   participant DicomStudy
   participant BIDS
   participant MRIQC
   participant BIDS-derivatives
   end

   box Green Centralized Gitlab
   participant BIDS-fed
   participant BIDS-derivatives-fed
   end

   MRI Scanner ->> Mercure: send dicom
   Mercure ->> DicomStudy: init
   Mercure ->> BIDS: init

   loop Every new session
   Mercure ->> DicomStudy: add session as submodule
   DicomStudy ->> BIDS: trigger heudiconv
   BIDS ->>+BIDS: open MR
   activate BIDS
   BIDS ->> BIDS: test: bids-validator
   BIDS ->> BIDS: test: protocol compliance
   BIDS ->> BIDS: run: defacing
   BIDS ->> MRIQC: trigger: mriqc
   MRIQC ->> BIDS: include/add link to reports in MR
   create actor A as Dataset Admin
   BIDS ->>-A: Notify
   A ->> BIDS: Review + (Fix) + merge MR
   loop For each configured preproc pipelines
   BIDS ->>+BIDS-derivatives: trigger preproc newly merged session
   BIDS-derivatives ->> BIDS-derivatives: open MR (preproc reports as artifacts)
   BIDS-derivatives ->>-A: Notify
   A ->> BIDS-derivatives: Review reports + merge MR
   end
   end
   A ->> BIDS: Create release
   BIDS ->> BIDS-fed: Push git + "green" data (minio)
   A ->> BIDS-derivatives: Create release
   BIDS-derivatives ->> BIDS-derivatives-fed: Push git + "green" data (minio)

As we can see in the diagram the data flow is divided into 3 parts.

1) Data acquisition in DICOM format which will be pushed to the Mercure instance. The data is then automatically pushed to the local GitLab instance.

2) Local GitLab git flow illustrates the workflow, starting from the push of a new DICOM session to executing data conversion and processing.

3) Data integration and sharing using a centralized GitLab instance.

The dataset admin stick man corresponds the indiviudal responsable for QC reviewing, dataset merging and pipeline monitoring. These tasks can be divided into multiple individuals for more efficient and robust management.

We utilize DICOM networking protocol to transfer the images from the scanner to the data server Mercure instance where it gets archived and automatically pushed to the GitLab instance based on the following DICOM tags:

- **ReferringPhysicianName:** This determines the Principal Investigator Name and corresponds to the root GitLab group name for the hierarchical structure of the dataset. 
- **StudyDescription:** This determines the study name and it corresponds to the following sub-group name in the hierarchical structure of the dataset.
- **StudyInstanceUID:** This determines the unique dicom study ID and it is used to track the dicom data in GitLab.
- **PatientID:** This determines the BIDS unique participant ID and session IDs and it is used to create link the DICOM data to the BIDS dataset.

Tecnically speaking, mercure can receive data from any MRI vendor, however, it has been only been configured to work with either a Siemens or GE 3T MRI scanner yet. This can be addapted to any scanner vendor with a bit of work and testing.

.. note:: 

    The selected DICOM tags can be modified to adapt to the restrictions of the acquisition site. Nevertheless, it is adviced to reliably have enough information in the tags to be able to create an equivalent structure. 

Git Flow
^^^^^^^^

Using DataLad for data version control enables tracking the provenance of datasets from their creation to their sharing. This is achieved through a Git flow approach, where changes to the dataset are stored in separate branches and merged when ready.

The previous :ref:`sequence diagram<diagram>` illustrates the workflow, starting from the push of a new DICOM session to executing data processing and release mechanisms on the federated instance (details to be designed).

Each GitLab actor/repository (e.g., DicomStudy, BIDS, Derivatives) is specific to a study, as defined by the DICOM tag `StudyDescription` (e.g., C-PIP). Each study follows this structure within a GitLab group, organized under groups corresponding to the local Principal Investigator or local consortia.

All operations on GitLab are automated through GitLab pipelines, executed as CI jobs by the GitLab runners and can be divided into different phases.

Pilot Phase
~~~~~~~~~~~

During the pilot phase, an experimenter will acquire one or multiple sessions to test sequences and/or full protocol. When the sessions are labelled as ``dev`` or ``pilot`` in the ``PatientID`` these are considered pilot sessions. The pilot sessions are converted to BIDS as regular session but open a `Merge Request (MR)` to the `pilot branch`. That MR triggers the same workflow as for sessions in the production phase, including BIDS-validation, defacing, and MRIQC: all useful to examine the compliance and quality of the data.

Once merged to the pilot branch they also trigger:

  - A configuration of the `forbids <https://github.com/UNFmontreal/forbids>`_ tool that will enforce the protocol in future sessions.

  - A configuration of standard pre-processing pipelines based on the acquired data.

  - Standard pre-processing pipelines are then triggered to check if the pilot data are compatible and produce sensible results.

The merge of new sessions iterating on the protocol reconfigure the protocol and pipelines, and also opens a `Merge Request` from the `cherry-picked` configs on `config` to the `base` branch. When the protocol is finalized and all checks pass, that MR with the latest config is to be reviewed, manually edited if necessary, and merged, effectively setting-up the repo for tests and derivatives generation during the production phase.

.. mermaid::

    %%{ init: { "theme": "forest" } }%%
    gitGraph:
        commit "start"
        branch config
        branch base
        checkout base
        commit id:"zzzzzzzzzzz"

        branch pilot
        checkout base                    

        branch convert/pilot1
        checkout convert/pilot1
        commit id:"heudiconv"
        commit id:"post-heudiconv-fixes"
        commit id:"fill-intendedfor/b0field"
        commit id:"deface"

        checkout pilot
        merge convert/pilot1
        commit id:"configs"

        checkout config
        cherry-pick id:"configs"

        checkout base
        commit id:"to better align"

        branch convert/pilot2
        checkout convert/pilot2
        commit id:"heudiconv-2"
        commit id:"post-heudiconv-fixes-2"
        commit id:"fill-intendedfor/b0field-2"
        commit id:"deface-2"

        checkout pilot
        merge convert/pilot2
        commit id:"reconfigs"

        checkout config
        cherry-pick id:"reconfigs"

        checkout base
        merge config

        checkout main
        merge base

Production Phase
~~~~~~~~~~~~~~~~

During the production phase, new sessions are `converted` into separated ``convert/{session_name}`` branches and open new Merge Requests with tests / QC reports to be reviewed and edited if necessary, before merging into the `dev` branch.

.. mermaid::

    %%{ init: { "theme": "forest" } }%%
    gitGraph:
        commit "start"

        branch base
        checkout base
        commit id:"zzzzzzzzzzz"

        branch dev
        checkout base

        branch convert/session_name1
        checkout convert/session_name1
        commit id:"heudiconv"
        commit id:"post-heudiconv-fixes"
        commit id:"fill-intendedfor/b0field"
        commit id:"deface"

        checkout dev
        merge convert/session_name1

        checkout base
        branch convert/session_name2
        checkout convert/session_name2
        commit id:"heudiconv-2"
        commit id:"post-heudiconv-fixes-2"
        commit id:"fill-intendedfor/b0field-2"
        commit id:"deface-2"

        checkout dev
        merge convert/session_name2

Release Phase
~~~~~~~~~~~~~

When working on a data-release, a new release branch can be created from ``dev``, iterated upon (eg. edit README, docs, ) through branches and MRs, and finally merge to the ``main`` branch and tagged with a release version.
New sessions continues to be added to the ``dev`` branch in the back.


.. mermaid::

    %%{ init: { "theme": "forest" } }%%
    gitGraph:
        branch dev
        checkout main
        commit
        commit id:"previous_release" tag:"rel/www"

        checkout dev
        commit id:"long history"
        commit id:"bunch_of_sessions_now"

        branch rel/xxx
        checkout rel/xxx

        branch fix/xyz
        checkout dev
        commit
        commit

        checkout fix/xyz
        commit id:"random-fix"
        checkout rel/xxx
        merge fix/xyz

        checkout dev
        commit
        commit

        checkout rel/xxx
        branch fix/zyx
        checkout fix/zyx
        commit id:"edit README"
        checkout rel/xxx
        merge fix/zyx

        checkout main
        merge rel/xxx tag:"rel/xxx"

        checkout dev
        commit


Pipeline Management
^^^^^^^^^^^^^^^^^^^

Automated
~~~~~~~~~~

After proper configurations have been made, the data ingestion process is fully automated. The data is pushed to the Mercure instance and automatically pushed to the local GitLab instance. The data is then converted to BIDS format and processed using the configured pipelines.

Heudiconv Conversion to BIDS
============================

The Heudiconv tool is used to convert DICOM files to BIDS format following a set of heuristics that define how the data should be organized.

The heuristics file is a Python script that can be found in `ci-pipelines BIDS-flux repository <https://gitlab.unf-montreal.ca/bids-flux/ci-pipelines/-/blob/main/src/pipelines/mri/heuristics_cpip.py?ref_type=heads>`_.

In general the heuristics file is configured to run multiple functions:

- **def custom_seqinfo(wrapper, series_files):** This function is used to extract the relevant DICOM tags from the DICOM files that will be used to determine the BIDS sequence information.
- **def infotoids(seqinfos, outdir):** This function leverages the extracted DICOM tags to determine the BIDS subject and session IDS.
- **def infotodict(seqinfo):** Heuristic evaluator for determining which runs belong where allowed template fields follow python string module.

Deface of BIDS images
============================

The defacing of BIDS images is performed using a simple custom tool that affinely registers the T1w image to the MNI spcase and applies a mask to the image.

BIDS-validation
============================

The BIDS-validation process is performed using the dockerized version of the `BIDS-validator tool <https://hub.docker.com/r/bids/validator>`_, which checks the newly created BIDS dataset for compliance with the BIDS standard. This step is repeated for every change made to the BIDS datalad dataset in GitLab.

MRIQC
============================

The MRIQC tools is used to asses the quality of the BIDS images. The MRIQC reports are generated and stored in the ``qc/mriqc`` datalad dataset in gitlab. The reports are linked to the BIDS images, allowing for easy access and review through the merge request.

Manual Input
~~~~~~~~~~~~

The dataset administrator is responsible for reviewing the BIDS-converted data and associated MRIQC reports. They may also manually edit the BIDS dataset when necessary. Additionally, the administrator oversees the approval process for merge requests, ensuring that any required modifications are made prior to granting approval.

Retiggering of Heudiconv
============================

If the Heudiconv conversion process fails or requires reconfiguration of the heuristics, the dataset administrator can manually trigger the process again using the GitLab interface. This allows for flexibility in managing the conversion process and ensuring that the data is properly formatted.

.. note:: 

    If the DICOM data was partially converted causing the pipeline to fail the BIDS-validation and a new ``convert/sub-1_ses-1`` branch was created. You will need to either change the branch name to something like ``convert/sub-1_ses-1_originalconv`` or delete it as the retrigger process will try to recreate the same branch as before failing in the process. 
    
    The partially converted data will be kept in the S3 compatible storage (MinIO) unless you delete it manually. You can delete it using a combination of git, git-annex, and datalad with the following command:

    .. code-block:: bash

        git checkout convert/sub-1_ses-1
        git annex drop --from=<remote name> /path/to/data --force
        datalad save --message "deleted partial conversion data"

    The reason we need to save the changes after the fact is that git-annex needs to be notified that you dropped the binary data from the remote. Otherwise when reconverting the data, datalad might think the data already exists in the remote and not upload the complete data.

Manual Editing of BIDS Dataset
============================

The dataset administrator can manually edit the BIDS dataset using git and Datalad commands. This allows for flexibility in managing the dataset and ensuring that it meets the BIDs standards.

.. code:: bash

    git mv /path/to/file /new/path/to/file
    datalad save --message "Renamed files"
    git rm /path/to/file
    datalad save --message "Deleted files"
    datalad push --to=origin
    datalad push --to=<bids s3 remote>


MRIQC Report & Merge Request Review
============================

The MRIQC reports will need to be reviewed by the dataset administrator. Depending on the project needs the dataset administrator can choose to either approve the merge request of new ``convert/sub-1_ses-1`` to the ``dev`` branch or reject it.

Data Access
^^^^^^^^^^^

Access Management
============================

Access to the data is managed through GitLab groups and S3 bucket policies. This access can be as granular as the project requires. The dataset administrator is responsible for managing access to the data, including granting and revoking permissions as needed. Access to the data is typically restricted to authorized personnel only, ensuring that sensitive information is protected. When data is ready to be shared openly or with specific collaboration groups or individuals, the dataset administrator can create a release branch and tag it with a version number.

Different tiers of access using gitlab can be reviewed in the `official GitLab documentation <https://docs.gitlab.com/user/permissions/>`_.

S3 bucket policies can be used to restrict access to the data stored in MinIO. The dataset administrator can create policies that allow or deny access to specific users or groups based on their roles and responsibilities. This ensures that only authorized personnel have access to sensitive data, while still allowing for collaboration and sharing of non-sensitive data. 

Locally
~~~~~~~
GitLab serves as a catalogue for the BIDS-flux data. 

To access data from the BIDS-flux infrastructure you will need to work with two of the software applications deployed for BIDS-flux, GitLab and MinIO. 

GitLab tracks the structure and history of the repositories, or in our case, the study directory hierarchy. The hierarchy of directories inside of GitLab is defined in this order: **Principal Investigator** / **Study Name** / (``bids``, ``sourcedata``, ``qc``, ``derivatives``). **Principal Investigator** will be the investigator who is heading the study. **Study Name** will be the name of the study or studies which are under the principal investigator. Under each independent study, you will find 4 different repositories containing study-specific data. The ``sourcedata`` repository will be the one keeping track of all the DICOM files of the study. The ``bids`` folder tracks the BIDS formatted images for the study. The ``qc`` repository tracks the quality control checks for the data of the study, and the ``derivatives`` repository tracks processing steps for the BIDS formatted data.

MinIO will serve as the object storage for all the data for the repositories in GitLab. 
GitLab track the file’s history and the structure while MinIO stores all the images and binary objects (all non-text files).

