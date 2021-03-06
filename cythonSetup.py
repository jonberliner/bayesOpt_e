from distutils.core import setup
from distutils.extension import Extension
import numpy
from Cython.Distutils import build_ext
setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [
        # Extension("jbgp", ["jbgp.pyx"]),
        Extension("jbgp_1d", ["jbgp_1d.pyx"])
    ],
    include_dirs=[numpy.get_include()]
)
