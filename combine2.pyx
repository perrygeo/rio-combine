# http://gis.stackexchange.com/questions/120102/fast-raster-combine-using-rasterio
import cython
import numpy as np
cimport numpy as np

@cython.boundscheck(False)
cpdef object combine_rasters(list in_rasters):
    """
    Given a list of input rasters, produce a combined raster that represents
    the unique combinations found across these rasters.  A unique value is
    given to each unique combination and a dictionary stores the relationship
    between the unique combination and the output value in the combined
    raster.

    For now, stupidly assume that all rasters have exactly the same
    window and cellsize.

    Parameters
    ----------
    in_rasters: list of rasterio.RasterReader objects
        The list of input rasters from which to find unique combinations

    Returns
    -------
    out_arr: np.ndarray
        The output array that holds a unique value for each unique combination
        in in_rasters.

    out_dict: dict
        The mapping of unique combination (tuple as the key) to output value
        (integer as the value)
    """

    # Get the number of rows and columns and block sizes
    cdef unsigned int x_size = in_rasters[0].height
    cdef unsigned int y_size = in_rasters[0].width
    cdef unsigned int x_block_size = in_rasters[0].block_shapes[0][0]
    cdef unsigned int y_block_size = in_rasters[0].block_shapes[0][1]

    # Define local variables
    cdef unsigned int n = len(in_rasters)
    cdef np.ndarray[np.uint32_t, ndim=3] in_arr = np.empty(
        (x_block_size, y_block_size, n), dtype=np.uint32)
    cdef np.ndarray[np.uint32_t, ndim=2] out_arr = np.empty(
        (x_size, y_size), dtype=np.uint32)
    cdef int x_wsize, y_wsize, x_start, y_start
    cdef int x, y, index = 0
    cdef dict d = {}
    cdef tuple t

    # Get a generator for iterating over the blocks in the raster
    blocks = in_rasters[0].block_windows()

    # Iterate over blocks
    for (_, window) in blocks:

        # Bring in a block's worth of data from all in_rasters
        in_arr = np.dstack(
            [in_rasters[i].read(1, window=window, masked=False) \
                for i in xrange(n)]).astype(np.uint32)

        # Find dimensions of this block
        x_start = window[0][0]
        y_start = window[1][0]
        x_wsize = window[0][1] - x_start
        y_wsize = window[1][1] - y_start

        # Iterate over rows and columns in this block
        for x in xrange(x_wsize):
            for y in xrange(y_wsize):
                t = tuple(in_arr[x, y])
                if t not in d:
                    d[t] = index
                    index += 1
                out_arr[x_start + x, y_start + y] = d[t]

    # Return the output numpy array and the lookup dictionary
    return out_arr, d
