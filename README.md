# Rasterio Combine

Implementation of the [combine operation](http://resources.arcgis.com/en/help/main/10.2/index.html#/Combine/009z0000007r000000/)

**Note: this is a work in progress; the core numpy function (`combine_rasters_df`) is working but eventually this will be rio plugin**

## Overview

Given two arrays of equal shape (i.e. raster data with the same spatial referencing, origin, shape and cellsize):

```
a = np.array(
    [[10, 12, 12, 12],
     [12, 12, 12, 11],
     [12, 10, 10, 11]])

b = np.array(
    [[20, 22, 21, 22],
     [21, 21, 22, 22],
     [20, 21, 22, 21]])

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
## Implementation

Instead of using tuples to describe pairs of array values, we can use the [Cantor pairing function](http://en.wikipedia.org/wiki/Pairing_function#Cantor_pairing_function) to encode/decode two integers to a single integer.

This allows us to use simple algebraic expressions with the highly optimized [`numexpr`](https://github.com/pydata/numexpr/wiki/Numexpr-Users-Guide) library.

## Caveats

The `combine_arrays_df` function will probably be renamed at some point.

There are some constraints of this implementation that you should be aware of:

* Input arrays
    * must have same shape, are assumed to have the exact same spatial referencing, etc.
    * must be integers, 16-bit or less, due to limitations in Cantor pairing algorithm implementation. Even `long`s start to overflow when input integers get up to 2**27, so 32 bit ints are not safe.
* Can only process two arrays at a time (n-value cantor "pairing" is not implemented yet)
* Output cell values are not contiguous or human-readable (but they are interpretable as a Cantor pair and this can be `depair`ed easily)
* No unit tests (yet)
* Unknown results when using masked arrays (nodata values)

## Performance

Compare to http://gis.stackexchange.com/questions/120102/fast-raster-combine-using-rasterio

```
$ python combine.py
generating test rasters...
benchmarking...
0.296485185623 combine_arrays_df (uses numexpr and cantor pairing, outputs pandas df)
0.26175403595 combine_arrays (uses numexpr and cantor pairing)
9.00938606262 combine_rasters (uses Cython and tuples)
-- numexpr version is 34.4x faster than cython version
Testing on 500x500 random values
OK
```
