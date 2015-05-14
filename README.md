# Rasterio Combine

Implementation of the [combine operation](http://resources.arcgis.com/en/help/main/10.2/index.html#/Combine/009z0000007r000000/)

## Overview

Given two arrays of equal shape (i.e. raster data with the same spatial referencing, origin, shape and cellsize):

```
a = np.array(
    [[10 12 12 12]
     [12 12 12 11]
     [12 10 10 11]])

b = np.array(
    [[20 22 21 22]
     [21 21 22 22]
     [20 21 22 21]]])

comb, df = combine_rasters_df(a, b)
```

The output `comb` array contains unique identifiers

```
[[ 485.  617.  582.  617.]
 [ 582.  582.  617.  583.]
 [ 548.  517.  550.  549.]]
```

Where the uids correspond to the indicies in `df` (a pandas dataframe)
and describe both input raster values and their counts:

```
     raster1  raster2  count
485       10       20      1
517       10       21      1
548       12       20      1
549       11       21      1
550       10       22      1
582       12       21      3
583       11       22      1
617       12       22      3
```

## Performance
Compare to http://gis.stackexchange.com/questions/120102/fast-raster-combine-using-rasterio

```
$ python combine.py
generating test rasters...
benchmarking...
0.326760053635 combine_arrays_df (uses numexpr and cantor pairing, outputs pandas df)
0.306179046631 combine_arrays (uses numexpr and cantor pairing)
7.90722513199 combine_rasters (uses Cython and tuples)
-- numexpr version is 25.8x faster than cython version
Testing on 500x500 random values
OK
```
