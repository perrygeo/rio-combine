from distutils.core import setup
from Cython.Build import cythonize
import numpy as np

setup(
    name = "combine2",
    ext_modules = cythonize('combine2.pyx'),  # accepts a glob pattern
    include_dirs = [np.get_include()],   
)
