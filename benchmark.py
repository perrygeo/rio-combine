from __future__ import print_function
import rasterio
import time
import random

from combine import read_data, combine_arrays, \
                    combine_arrays_df, write_random_rasters
from combine2 import combine_rasters


if __name__ == "__main__":
    print("generating test rasters...")
    p1, p2 = write_random_rasters(2000, 3000)

    print("benchmarking...")
    # Alternative: note 2rd return value: a dataframe with values as index
    # ----------- Numexpr w/df------------------------------
    start = time.time()
    a1, a2 = read_data(p1, p2)
    comb3, df3 = combine_arrays_df(a1, a2)
    print(time.time() - start, "combine_arrays_df (uses numexpr and cantor pairing, outputs pandas df)")

    # ----------- Numexpr ------------------------------
    start = time.time()
    a1, a2 = read_data(p1, p2)
    comb1, vat1 = combine_arrays(a1, a2)
    t1 = time.time() - start
    print(t1, "combine_arrays (uses numexpr and cantor pairing)")

    # ----------- Cython -------------------------------
    start = time.time()
    with rasterio.drivers(CPL_DEBUG=True):
        with rasterio.open(p1, 'r') as src1:
            with rasterio.open(p2, 'r') as src2:
                comb2, vat2 = combine_rasters([src1, src2])
    t2 = time.time() - start
    print(t2, "combine_rasters (uses Cython and tuples)")
    print("-- numexpr version is {}x faster than cython version".format(round(t2/t1, 1)))

    # ----------- Test ----------------------------------
    # Swap values and keys for easier lookup by cell value
    swpvat1 = dict(zip(vat1.values(), vat1.keys()))
    swpvat2 = dict(zip(vat2.values(), vat2.keys()))
    print("Testing on 500x500 random values")
    for x in [random.randint(0, comb2.shape[0]) in range(500)]:
        for y in [random.randint(0, comb2.shape[1]) in range(500)]:
            assert swpvat1[comb1[x, y]] == swpvat2[comb2[x, y]]
    print("OK")
