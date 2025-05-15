.. _datasets-index:

Datasets
========

All functional and anatomical data for the C-PIP project has been formatted in [BIDS](https://bids.neuroimaging.io/), for more information visit the Brain Imaging Data Structure documentation [site](https://bids-specification.readthedocs.io/en/stable/).

Note that BIDS session names have no meaning apart from being data acquired in the same session. The number of runs, the tasks and their order within each session will not match from one participant to another. Note that a few session indices are skipped if the whole session was discarded for various scanning issues.
<<<<<<<< HEAD:source/mri/datasets/index.rst
========

## Participants

C-PIP is a multisite study acquiring data from different target population. We generated 750 codes which are split across three sites. Using redcap we do the following. When a new participant joins the study their personal idenfiying information is recorded (e.g. name, contact information, etc.). This gives them a recruitment ID which triggers the the next step which is the consent form


```markdown
# Generating and Managing Subject IDs in REDCap

In REDCap (Research Electronic Data Capture), generating subject IDs for a multi-site study, separating recruitment IDs from consented IDs, and creating family IDs can be managed through a combination of REDCap's built-in features and custom project setup. Here’s a general approach:

## 1. Subject ID Generation for Multi-Site Studies

To generate unique subject IDs for a multi-site study, you can use a combination of automated numbering and site-specific prefixes. Here’s a step-by-step approach:

### A. Site-Specific Prefixes

- **Site Code:** Assign a unique code or prefix for each site (e.g., SITE1, SITE2).
- **Automated Numbering:** Use REDCap’s automated numbering feature to generate a sequential ID for each new record.

**Example:**

- For a participant from Site 1: `SITE1-001`, `SITE1-002`
- For a participant from Site 2: `SITE2-001`, `SITE2-002`

### B. Implementing in REDCap

1. **Create a Field for Site Code:**
   - Add a dropdown field (e.g., `site_code`) to select the site.

2. **Use Auto-Numbering for IDs:**
   - Enable auto-numbering in project settings for the record ID field.
   **Use a preregistered ID:**
   - Alternatively, pre-generate a list of subject IDs for each site which is used when creating the records in REDCap.

3. **Create a Calculated Field for Subject ID:**
   - Use a calculated field to concatenate the site code with the auto-numbered ID.
   - Formula: `[site_code] + '-' + [record_id]`

## 2. Separating Recruitment IDs from Consented IDs

To manage recruitment and consented IDs separately:

### A. Recruitment IDs

- **Recruitment ID:** Create a recruitment ID during the initial contact or pre-screening phase.

### B. Consented IDs

- **Consented ID:** Generate a new ID upon obtaining consent, possibly using the site-specific prefix system.

**Steps:**

1. **Recruitment Phase:**
   - Create a separate form for recruitment data with a unique recruitment ID.
   - Store preliminary information before consent.

2. **Consented Phase:**
   - After obtaining consent, create a new record in the main study database.
   - Link recruitment ID to the new consented ID for reference.

## 3. Generating Family IDs

For studies involving parent-child pairs or families:

### A. Family ID Field

- **Family ID:** Create a field to assign a unique family ID that can link all family members.

**Steps:**

1. **Create a Family ID Field:**
   - Add a field (e.g., `family_id`) to assign a family ID.
   - Generate this ID manually or using a combination of site code and a sequential number (e.g., `FAM001`, `FAM002`).

2. **Linking Family Members:**
   - Ensure each family member’s record includes the same family ID to link them.

## Implementation in REDCap

**Example Project Setup:**

1. **Create Fields:**
   - `site_code` (Dropdown): To select site.
   - `record_id` (Auto-Numbering): REDCap’s built-in ID.
   - `subject_id` (Calculated): `[site_code] + '-' + [record_id]`
   - `recruitment_id` (Text): Manually entered during recruitment.
   - `family_id` (Text): Manually or auto-generated to link family members.

2. **Form Design:**
   - **Recruitment Form:** Collects preliminary data with `recruitment_id`.
   - **Main Study Form:** Collects detailed data with `subject_id` and `family_id`.

3. **Workflow:**
   - **Recruitment Phase:** Use the recruitment form to gather initial data.
   - **Consent Phase:** Create a new record in the main study form, using `site_code` and auto-numbering for `subject_id`, and include the `family_id` for related participants.

This approach ensures unique and traceable IDs for participants across multiple sites, maintains separation between recruitment and consented IDs, and facilitates linking family members in the study.
```

## anat
>>>>>>>> main:source/DATASETS.md
