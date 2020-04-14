# HCUP-US-EHR 

This repo contains a simple script for downloading HCUP clinical code maps for diagnoses (ICD9) and CPTEVENTS.

In longitudinal EHR data clinical codes assigned to patients generally fall under a broader category and as there are limited data for each set of codes it may be useful to decrease the sparsity by grouping the codes under their common ancestor. 

Here we use two tools provided by [HCUP-US](https://www.hcup-us.ahrq.gov/) to achieve this:
- CCS/AppendixASingleDx.txt 
- 2019_ccs_services_procedures

Refer to [here](https://www.hcup-us.ahrq.gov/toolssoftware/ccs/ccs.jsp) for a description of the above.


## Usage
`python hcups_utils.py -t CPT --save_path ./data`


`python hcups_utils.py -t ICD9 --save_pah ./data`

## Mapping Proc To CCS

There are different ways of mapping Procedure codes, for exaple using crosswalk. 
In `MappingProcToCCS.ipynb` i've outlined how to do using an external tool. Check it out if you're interesd.

