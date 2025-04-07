# plotextractor


## About

A small library for extracting plots used in scholarly communication.

## Install

``` console
$ pip install plotextractor
```

## Usage

To extract plots from a tarball:

``` python
>>> from plotextractor import process_tarball
>>> plots = process_tarball('./1503.07589.tar.gz')
>>> print(plots[0])
{
    'captions': [
        u'Scans of twice the negative log-likelihood ratio $-2\\ln\\Lambda(\\mH)$ as functions of the Higgs boson mass \\mH\\ for the ATLAS and CMS combination of the \\hgg\\ (red), \\hZZllll\\ (blue), and combined (black) channels. The dashed curves show the results accounting for statistical uncertainties only, with all nuisance parameters associated with systematic uncertainties fixed to their best-fit values. The 1 and 2 standard deviation limits are indicated by the intersections of the horizontal lines at 1 and 4, respectively, with the log-likelihood scan curves.',
    ],
    'label': u'figure_LHC_combined_obs',
    'name': 'LHC_combined_obs_unblind_final',
    'original_url': './1503.07589.tar.gz_files/LHC_combined_obs_unblind_final.pdf',
    'url': './1503.07589.tar.gz_files/LHC_combined_obs_unblind_final.png',
}
```

## Notes

If you experience frequent `DelegateError` errors you may need to update
your version of GhostScript.

## License
GPLv2

## Local Development

Build it using
```shell
# python 2.7
docker build -t plotextractor2 -f Dockerfile.py2 .
# python 3.11
docker build -t plotextractor3 -f Dockerfile.py3 .
```
Spin up container with library installed
```shell
# python 2.7
docker run -it -v ./tests:/code/tests -v ./plotextractor:/code/plotextractor --name plotextractor2 plotextractor2
# python 3.11
docker run -it -v ./tests:/code/tests -v ./plotextractor:/code/plotextractor --name plotextractor2 plotextractor3
```
Run tests
```
pytest .
```



