# Study of Clear Sky Models for Singapore

With the spirit of reproducible research, this repository contains all the codes required to produce the results in the manuscript: S. Dev, S. Manandhar, Y. H. Lee and S. Winkler, Study of Clear Sky Models for Singapore, *Proc. Progress In Electromagnetics Research Symposium (PIERS)*, 2017. 

Please cite the above paper if you intend to use whole/part of the code. This code is only for academic and research purposes.

![alt text](https://github.com/Soumyabrata/clear-sky-models/blob/master/Figs/sample-solar-day.png "sample solar irradiance")

## Code Organization
The codes are written in python.

### Dataset
The required dataset are present in this repository. The weather station data are present in the folder `weather_data`, and the SODA files are present in the folder `soda_files`. 

### Core functionality
* `Bird_model.py` Estimates the solar radition values based on Bird's clear sky model.
* `import_WS.py` Imports the weather station data (format based on Davis weather station). 
* `nearest.py` Finds the nearest observation, based on a given time stamp. It also provides the timestamp difference between the queried- and found- timestamp. 
* `process_SODA.py` Processes the SODA McClear files.
* `RMSE.py` Calculates the RMSE between two numpy arrays. 
* `Yang_model.py` Estimates the solar radition values based on Yang's clear sky model.

### Reproducibility 
In addition to all the related codes, we have also shared sample generated clear-sky model for a single day. This can be found in the folder `./Figs`.

Please run the notebook `main.ipynb` to generate the various results mentioned in the paper.

