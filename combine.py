from __future__ import print_function
import numpy as np
import pandas as pd
import rasterio
import numexpr as ne
from pairing import depair


def build_flatlist(vat, count):
    result = {}
    for k, v in vat.items():
        result[k] = list(v)
    for k, v in count.items():
        result[k].append(count[k])
    return result


def write_random_rasters(x, y):
    ndA, ndB = read_random_data(x, y)

    kwargs = {
        'driver': 'GTiff',
        'width': ndA.shape[1],
        'height': ndA.shape[0],
        'count': 1,
        'dtype': rasterio.uint16,
    }

    with rasterio.open('tmpa.tif', 'w', **kwargs) as dst:
        dst.write_band(1, ndA)

    with rasterio.open('tmpb.tif', 'w', **kwargs) as dst:
        dst.write_band(1, ndB)

    return 'tmpa.tif', 'tmpb.tif'


def read_random_data(xsize=100, ysize=90):
    return (
        np.random.randint(10, 13, size=(ysize, xsize)).astype(np.uint16),
        np.random.randint(20, 23, size=(ysize, xsize)).astype(np.uint16))


def read_data(rasterA, rasterB):
    with rasterio.drivers():
        with rasterio.open(rasterA, 'r') as src:
            ndA = src.read(1)
        with rasterio.open(rasterB, 'r') as src:
            ndB = src.read(1)

    return ndA, ndB


def combine_arrays_df(a, b):
    """
    Uses Cantor pairing via numexpr for fast unique combinations
    Returns:
        ndarray with unique cell values
        pandas dataframe with cell values as index and raster vals and counts as columns
    Input constraints:
        same shape,
        uint16 or less (due to limitations in Cantor pairing algorithm)
        only 2 raster at a time (n-value cantor "pairing" is not implemented)
        output cell values are not contiguous or human-readable (but can be depaired easily)
    """
    assert a.shape == b.shape
    assert a.dtype in (np.int8, np.int16, np.uint8, np.uint16)

    # cantor pair as numexpr
    comb = ne.evaluate("0.5 * (a + b) * (a + b + 1) + b")

    # Get unique combinations and count them
    ucomb, counts = np.unique(comb, return_counts=True)
    counts_by_uid = dict(zip(ucomb, counts))

    # Value attribute table
    # maps tuples of unique value combinations to unique ids
    # (not used in this function but useful for comparison against
    # the data structure returned by @grovduck's combine)
    vat = dict(((depair(uid), uid) for uid in ucomb))

    # The vat keys/values are swapped to allow key lookup by uid
    swpvat = dict(zip(vat.values(), vat.keys()))
    # update into a flat list of values {id: [r1, r2, count]}
    lut = build_flatlist(swpvat, counts_by_uid)
    # and build pandas dataframe
    vatdf = pd.DataFrame(lut, index=['raster1', 'raster2', 'count']).T

    return comb, vatdf


def combine_arrays(a, b):
    """
    Uses Cantor pairing via numexpr for fast unique combinations
    constraints:
        same shape,
        uint16 or less (due to limitations in Cantor pairing algorithm)
        only 2 raster at a time (n-value cantor "pairing" is not implemented)
        output cell values are not contiguous or human-readable (but can be depaired easily)
    """
    import numexpr as ne
    import numpy as np
    from pairing import depair

    comb = ne.evaluate("0.5 * (a + b) * (a + b + 1) + b")
    ucomb, counts = np.unique(comb, return_counts=True)
    vat = dict(((depair(uid), uid) for uid in ucomb))
    return comb, vat

