# Correlating Satellite Cloud Cover with Sky Cameras

With the spirit of reproducible research, this repository contains all the codes required to produce the results in the manuscript: S. Manandhar, S. Dev, Y. H. Lee and Y. S. Meng, Correlating Satellite Cloud Cover with Sky Cameras, *Proc. Progress In Electromagnetics Research Symposium (PIERS)*, 2017. 

Please cite the above paper if you intend to use whole/part of the code. This code is only for academic and research purposes.

![alt text](https://github.com/Soumyabrata/MODIS-cloud-mask/blob/master/figs/cloudmask-result.png "cloud mask analysis")

## Code Organization
The codes are written in python. Thanks to <a href="https://www.linkedin.com/in/joseph-lemaitre-93a74412b/">Joseph Lemaitre</a> for providing the scripts to process MODIS multi bands images. 

### Dataset
The required dataset are present in this repository. The cloud mask data from MODIS satellite image are present in the folder `cloud_mask`, the combined cloud mask and cloud coverage data are present in the folder `cmask_coverage_result`, and the daywise cloud coverage data from sky cameras are present in the folder `coverage_data`. 

### Core functionality

* `nearest.py` Finds the nearest observation, based on a given time stamp. It also provides the timestamp difference between the queried- and found- timestamp. 
* `normalize_array.py` Normalizes a numpy array into the range [0,1]. 
* `readCoverage.py` Helper function to read and analyze all individual coverage files. 

### Reproducibility 
In addition to all the related codes, we have shared the analysis figure in the folder `./figs`.

Please run the notebook `main.ipynb` to generate the result mentioned in the paper.

