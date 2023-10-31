# MRI

## Image acquisition

### Scanner
Magnetic resonance imaging (MRI) for the Courtois neuromod project is being acquired at the functional neuroimaging unit ([UNF](https://unf-montreal.ca/)), located at the "Centre de Recherche de l'Institut Universitaire de Gériatrie de Montréal" ([CRIUGM](http://www.criugm.qc.ca/)) and affiliated with [University of Montreal](https://www.umontreal.ca/) as well as the [CIUSSS du Centre-Sud-de-l'île-de-Montréal](https://ciusss-centresudmtl.gouv.qc.ca/propos/services-en-anglais). The scanner is a Siemens Prisma Fit, equipped with a 2-channel transmit body coil and a 64-channel receive head/neck coil.

## Sequences

### Functional sequences

The parameters of the functional MRI sequence relevant for data analysis can be found in the C-PIP DataLad. The functional acquisition parameters are all identical to the one used in the dataset. The Siemens exam card can be found [here](./_static/mri/functional_protocol_HCP-trt.pdf), and is briefly recapitulated below. Functional MRI data was acquired using an accelerated simultaneous multi-slice, gradient echo-planar imaging sequence [(Xu et al., 2013)](http://www.ncbi.nlm.nih.gov/pubmed/23899722) developed at the Center for Magnetic Resonance Research (CMRR) University of Minnesota, as part of the Human Connectome Project [(Glasser et al., 2016)](https://www.nature.com/articles/nn.4361). The sequence is available on the Siemens PRISMA scanner at UNF through a concept to production (C2P) agreement, and was used with the following parameters: slice acceleration factor = 4, TR = 1.49 s, TE = 37 ms, flip angle = 52 degrees, voxel size = 2 mm x 2 mm x 2 mm, 60 slices, acquisition matrix 96x96. In each session, a short acquisition (3 volumes) with reversed phase encoding direction was run to allow retrospective correction of B0 field inhomogeneity-induced distortion.

### Brain anatomical sequences

 The parameters of the brain anatomical MRI sequences relevant for data analysis can be found in the NeuroMod DataLad. The acquisition parameters are identical for all anatomical sessions. The Siemens pdf exam card of the anatomical sessions can be found [here](./_static/mri/anatomical_protocol_2019-01-22.pdf), and is briefly recapitulated below. A standard (brain) anatomical session started with a 21 s localizer scan, and then included the following sequences:
  * T1-weighted MPRAGE 3D sagittal sequence (duration 6:38 min, TR = 2.4 s, TE = 2.2 ms, flip angle = 8 deg, voxel size = 0.8 mm isotropic, R=2 acceleration)
  * T2-weighted FSE (SPACE) 3D sagittal sequence (duration 5:57 min, TR = 3.2 s, TE = 563 ms, voxel size = 0.8 mm isotropic, R=2 acceleration)
  * Diffusion-weighted 2D axial sequence (duration 4:04 min, TR = 2.3 s, TE = 82 ms, 57 slices, flip angle = 78 deg, voxel size = 2 mm isotropic,  phase-encoding P-A, SMS=3 through-plane acceleration, b-max = 3000 s/mm2). The same sequence was run with phase-encoding A-P to correct for susceptibility distortions.
  * gradient-echo magnetization-transfer 3D sequence (duration 3:34 min, 28 = ms, TE = 3.3 ms, flip angle = 6 deg, voxel size = 1.5 mm isotropic, R=2 in-plane GRAPPA, MT pulse Gaussian shape centered at 1.2 kHz offset).
  * gradient-echo proton density 3D sequence (same parameters as above, without the MT pulse).
  * gradient-echo T1-weighted 3D sequence (same parameters as above, except: TR = 18 ms, flip angle = 20 deg).
  * MP2RAGE 3D sequence (duration 7:26 min, TR = 4 s, TE = 1.51 ms, TI1 = 700 ms, TI2 = 1500 ms, flip angle 1 = 7 deg, flip angle 2 = 5 deg, voxel size = 1.2 mm isotropic, R=2 acceleration)
  * Susceptibility-weighted 3D sequence (duration 4:54 min, TR = 27 ms, TE = 20 ms, flip angle = 15 deg)

.. warning::  T1w, T2w and DWI (from HCP development/aging protocol for Siemens Prisma) and SWI do not have gradient non-linearity correction applied on the scanner. Offline correction can be applied using tools such as [gradunwarp](https://github.com/Washington-University/gradunwarp), but is not included yet in fMRIPrep pipeline.

## Stimuli

### Visual presentation

All visual stimuli were projected using a Epson Powerlite L615U projector. The images were casted through a waveguide onto a blank screen located in the MRI room.

### Auditory system

For functional sessions, participant wore MRI compatible  S15 [Sensimetric](http://www.sens.com/products/model-s15/) headphone inserts, proving high-quality acoustic stimulation and substantial attenuation of background noise.  On the computer used for stimuli presentation, a custom impulse response of the headphones is applied with an online finite impulse response filter using the LADSPA DSP to all the presented stimuli.This impulse response was provided by the manufacturer. Sounds was amplified using an [AudioSource](http://audiosource.net/shop/amp100vs/) AMP100V amplifier, situated in the control room. Participants also wear custom sound protection gear (see section on Hearing protection above).

### Stimuli presentation

## Physiological measures

### Example 1

## Mock scanner
Some of our datasets required a comparison between genuine in-scanner conditions and "mock" conditions, where the subject was installed in a fake scanner that reproduced the comfort and aspect of an MRI scanner. This mock setup was also located at [UNF](https://unf-montreal.ca/), and was equipped with a monitor screen for stimulus presentation as well as audio headphones and response devices (keyboard and video game controller).
