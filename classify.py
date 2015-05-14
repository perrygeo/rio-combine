

def mk_classify(vat):
    def classify(x):
        """
        This gets called ALOT, once per pixel. Performance matters.
        """
        try:
            uc = tuple(x)
        except:
            uc = x
        try:
            return vat[uc]
        except KeyError:
            return None
    return classify


def create_expr(vat, aname):
    # ideally we could take counts to order by
    if not vat:          # base case
        return False
    else:                # recursive case
        item = vat[0]
        return "where({}=={},{},{})".format(
            aname,
            item[0],  # test value
            item[1],  # value if true
            create_expr(vat[1:], aname))


def intersect_flatlist(dicts):
    result = {}
    for d in dicts:
        for k, v in d.items():
            try:
                result.setdefault(k, []).extend(v)
            except TypeError:
                result[k].append(v)
    return result


def combine_arrays_bad(a, b):
    """
    requires numpy 1.9
    DO NOT USE ... buggy due to zipping key ordering blah blahh
    """
    # Must be integer arrays of the same shape
    assert a.shape == b.shape
    # assert a.dtype == np.int32

    # combined raster; tuples of (a,b) pairs
    comb = np.array(zip(a.ravel(), b.ravel()), dtype=('i8,i8')).reshape(a.shape)

    # Get unique combinations and count them
    ucomb, counts = np.unique(comb, return_counts=True)

    # Lookup table
    # keys: tuples of unique value combinations
    # vals: unique id
    vat = dict(zip(ucomb.tolist(), range(ucomb.size)))

    # # The vat keys/values are swapped to later allow key lookup by id
    swpvat = dict(zip(vat.values(), vat.keys()))

    # # map ids to cell counts
    vat_counts = dict(zip(vat.values(), counts))

    # # update into a flat list of values {id: [r1, r2, count]}
    flatlist = intersect_flatlist([swpvat, vat_counts])

    # # Build dataframe
    vatdf = pd.DataFrame(flatlist, index=['raster1', 'raster2', 'count']).T

    # Create a vectorized numpy function and classify the combined array
    # so that new cell values match indexes of the above dataframe
    classify = mk_classify(vat)
    vclassify = np.vectorize(classify)
    cls_comb = vclassify(comb)

    return cls_comb, vatdf

