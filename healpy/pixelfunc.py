# 
#  This file is part of Healpy.
# 
#  Healpy is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
# 
#  Healpy is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with Healpy; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# 
#  For more information about Healpy, see http://code.google.com/p/healpy
#
"""
=====================================================
pixelfunc.py : Healpix pixelization related functions
=====================================================

This module provides functions related to Healpix pixelization scheme.

conversion from/to sky coordinates
----------------------------------

- :func:`pix2ang` converts pixel number to angular coordinates
- :func:`pix2vec` converts pixel number to unit 3-vector direction
- :func:`ang2pix` converts angular coordinates to pixel number
- :func:`vec2pix` converts 3-vector to pixel number 
- :func:`vec2ang` converts 3-vector to angular coordinates
- :func:`ang2vec` converts angular coordinates to unit 3-vector
- :func:`get_neighbours` returns the 4 nearest pixels for given
  angular coordinates
- :func:`get_all_neighbours` return the 8 nearest pixels for given
  angular coordinates

conversion between NESTED and RING schemes
------------------------------------------

- :func:`nest2ring` converts NESTED scheme pixel numbers to RING
  scheme pixel number
- :func:`ring2nest` converts RING scheme pixel number to NESTED
  scheme pixel number
- :func:`reorder` reorders a healpix map pixels from one scheme to another

nside/npix/resolution
---------------------

- :func:`nside2npix` converts healpix nside parameter to number of pixel
- :func:`npix2nside` converts number of pixel to healpix nside parameter
- :func:`nside2resol` converts nside to mean angular resolution
- :func:`nside2pixarea` converts nside to pixel area
- :func:`isnsideok` checks the validity of nside
- :func:`isnpixok` checks the validity of npix
- :func:`get_map_size` gives the number of pixel of a map
- :func:`get_min_valid_nside` gives the minimum nside possible for a given
  number of pixel
- :func:`get_nside` returns the nside of a map
- :func:`maptype` checks the type of a map (one map or sequence of maps)
- :func:`ud_grade` upgrades or degrades the resolution (nside) of a map

Masking pixels
--------------

- :const:`UNSEEN` is a constant value interpreted as a masked pixel
- :func:`mask_bad` returns a map with ``True`` where map is :const:`UNSEEN`
- :func:`mask_good` returns a map with ``False`` where map is :const:`UNSEEN`
- :func:`ma` returns a masked array as map, with mask given by :func:`mask_bad`

Map data manipulation
---------------------

- :func:`fit_dipole` fits a monopole+dipole on the map
- :func:`fit_monopole` fits a monopole on the map
- :func:`remove_dipole` fits and removes a monopole+dipole from the map
- :func:`remove_monopole` fits and remove a monopole from the map
- :func:`get_interp_val` computes a bilinear interpolation of the map
  at given angular coordinates, using 4 nearest neighbours
"""

import numpy as npy
import exceptions
import warnings
import _healpy_pixel_lib as pixlib

#: Special value used for masked pixels
UNSEEN = pixlib.UNSEEN

__all__ = ['pix2ang', 'pix2vec', 'ang2pix', 'vec2pix',
           'ang2vec', 'vec2ang',
           'get_neighbours', 'get_interp_val', 'get_all_neighbours',
           'nest2ring', 'ring2nest', 'reorder', 'ud_grade',
           'UNSEEN', 'mask_good', 'mask_bad', 'ma',
           'fit_dipole', 'remove_dipole', 'fit_monopole', 'remove_monopole',
           'nside2npix', 'npix2nside', 'nside2resol',
           'nside2pixarea', 'isnsideok', 'isnpixok',
           'get_map_size', 'get_min_valid_nside',
           'get_nside', 'maptype']

def mask_bad(m, badval = UNSEEN, rtol = 1.e-5, atol = 1.e-8):
    """Returns a bool array with ``True`` where m is close to badval.

    Parameters
    ----------
    m : a map (may be a sequence of maps)
    badval : float, optional
        The value of the pixel considered as bad (:const:`UNSEEN` by default)
    rtol : float, optional
        The relative tolerance
    atol : float, optional
        The absolute tolerance

    Returns
    -------
    mask
      a bool array with the same shape as the input map, ``True`` where input map is
      close to badval, and ``False`` elsewhere.

    See Also
    --------
    mask_good, ma

    Examples
    --------
    >>> import healpy as hpy
    >>> m = npy.arange(12.)
    >>> m[3] = hpy.UNSEEN
    >>> hpy.mask_bad(m)
    array([False, False, False,  True, False, False, False, False, False,
           False, False, False], dtype=bool)
    """
    atol = npy.absolute(atol)
    rtol = npy.absolute(rtol)
    return npy.absolute(m - badval) <= atol + rtol * npy.absolute(badval)

def mask_good(m, badval = UNSEEN, rtol = 1.e-5, atol = 1.e-8):
    """Returns a bool array with ``False`` where m is close to badval.

    Parameters
    ----------
    m : a map (may be a sequence of maps)
    badval : float, optional
        The value of the pixel considered as bad (:const:`UNSEEN` by default)
    rtol : float, optional
        The relative tolerance
    atol : float, optional
        The absolute tolerance

    Returns
    -------
    a bool array with the same shape as the input map, ``False`` where input map is
    close to badval, and ``True`` elsewhere.

    See Also
    --------
    mask_bad, ma

    Examples
    --------
    >>> import healpy as hpy
    >>> m = npy.arange(12.)
    >>> m[3] = hpy.UNSEEN
    >>> hpy.mask_good(m)
    array([ True,  True,  True, False,  True,  True,  True,  True,  True,
            True,  True,  True], dtype=bool)
    """
    atol = npy.absolute(atol)
    rtol = npy.absolute(rtol)
    return npy.absolute(m - badval) > atol + rtol * npy.absolute(badval)

def ma(m, badval = UNSEEN, rtol = 1e-5, atol = 1e-8, copy = True):
    """Return map as a masked array, with ``badval`` pixels masked.

    Parameters
    ----------
    m : a map (may be a sequence of maps)
    badval : float, optional
        The value of the pixel considered as bad (:const:`UNSEEN` by default)
    rtol : float, optional
        The relative tolerance
    atol : float, optional
        The absolute tolerance
    copy : bool, optional
        If ``True``, a copy of the input map is made.

    Returns
    -------
    a masked array with the same shape as the input map, masked where input map is
    close to badval.

    See Also
    --------
    mask_good, mask_bad, numpy.ma.masked_values

    Examples
    --------
    >>> import healpy as hpy
    >>> m = npy.arange(12.)
    >>> m[3] = hpy.UNSEEN
    >>> hpy.ma(m)
    masked_array(data = [0.0 1.0 2.0 -- 4.0 5.0 6.0 7.0 8.0 9.0 10.0 11.0],
                 mask = [False False False  True False False False False False False False False],
           fill_value = -1.6375e+30)
    <BLANKLINE>
    """
    return npy.ma.masked_values(m, badval, rtol = rtol, atol = atol, copy = copy)

def ang2pix(nside,theta,phi,nest=False):
    """ang2pix : nside,theta[rad],phi[rad],nest=False -> ipix (default:RING)

    Parameters
    ----------
    nside : int, scalar or array-like
      The healpix nside parameter, must be a power of 2
    theta, phi : float, scalars or array-like
      Angular coordinates of a point on the sphere
    nest : bool, optional
      if True, assume NESTED pixel ordering, otherwise, RING pixel ordering

    Returns
    -------
    pix : int or array of int
      The healpix pixel numbers. Scalar if all input are scalar, array otherwise.
      Usual numpy broadcasting rules apply.

    See Also
    --------
    pix2ang, pix2vec, vec2pix

    Examples
    --------
    >>> import healpy as hpy
    >>> hpy.ang2pix(16, npy.pi/2, 0)
    1440

    >>> hpy.ang2pix(16, [npy.pi/2, npy.pi/4, npy.pi/2, 0, npy.pi], [0., npy.pi/4, npy.pi/2, 0, 0])
    array([1440,  427, 1520,    0, 3068])

    >>> hpy.ang2pix(16, npy.pi/2, [0, npy.pi/2])
    array([1440, 1520])

    >>> hpy.ang2pix([1, 2, 4, 8, 16], npy.pi/2, 0)
    array([   4,   12,   72,  336, 1440])
    """
    if nest:
        return pixlib._ang2pix_nest(nside,theta,phi)
    else:
        return pixlib._ang2pix_ring(nside,theta,phi)

def pix2ang(nside,ipix,nest=False):
    """pix2ang : nside,ipix,nest=False -> theta[rad],phi[rad] (default RING)

    Parameters
    ----------
    nside : int or array-like
      The healpix nside parameter, must be a power of 2
    ipix : int or array-like
      Angular coordinates of a point on the sphere
    nest : bool, optional
      if True, assume NESTED pixel ordering, otherwise, RING pixel ordering

    Returns
    -------
    theta, phi : float, scalar or array-like
      The angular coordinates corresponding to ipix. Scalar if all input
      are scalar, array otherwise. Usual numpy broadcasting rules apply.

    See Also
    --------
    ang2pix, vec2pix, pix2vec

    Examples
    --------
    >>> import healpy as hpy
    >>> hpy.pix2ang(16, 1440)
    (1.5291175943723188, 0.0)

    >>> hpy.pix2ang(16, [1440,  427, 1520,    0, 3068])
    (array([ 1.52911759,  0.78550497,  1.57079633,  0.05103658,  3.09055608]), array([ 0.        ,  0.78539816,  1.61988371,  0.78539816,  0.78539816]))

    >>> hpy.pix2ang([1, 2, 4, 8], 11)
    (array([ 2.30052398,  0.84106867,  0.41113786,  0.2044802 ]), array([ 5.49778714,  5.89048623,  5.89048623,  5.89048623]))
    """
    if nest:
        return pixlib._pix2ang_nest(nside, ipix)
    else:
        return pixlib._pix2ang_ring(nside,ipix)

def vec2pix(nside,x,y,z,nest=False):
    """vec2pix : nside,x,y,z,nest=False -> ipix (default:RING)

    Parameters
    ----------
    nside : int or array-like
      The healpix nside parameter, must be a power of 2
    x,y,z : floats or array-like
      vector coordinates defining point on the sphere
    nest : bool, optional
      if True, assume NESTED pixel ordering, otherwise, RING pixel ordering

    Returns
    -------
    ipix : int, scalar or array-like
      The healpix pixel number corresponding to input vector. Scalar if all input
      are scalar, array otherwise. Usual numpy broadcasting rules apply.

    See Also
    --------
    ang2pix, pix2ang, pix2vec

    Examples
    --------
    >>> import healpy as hpy
    >>> hpy.vec2pix(16, 1, 0, 0)
    1504

    >>> hpy.vec2pix(16, [1, 0], [0, 1], [0, 0])
    array([1504, 1520])

    >>> hpy.vec2pix([1, 2, 4, 8], 1, 0, 0)
    array([  4,  20,  88, 368])
    """
    if nest:
        return pixlib._vec2pix_nest(nside,x,y,z)
    else:
        return pixlib._vec2pix_ring(nside,x,y,z)

def pix2vec(nside,ipix,nest=False):
    """pix2vec : nside,ipix,nest=False -> x,y,z (default RING)

    Parameters
    ----------
    nside : int, scalar or array-like
      The healpix nside parameter, must be a power of 2
    ipix : int, scalar or array-like
      Healpix pixel number
    nest : bool, optional
      if True, assume NESTED pixel ordering, otherwise, RING pixel ordering

    Returns
    -------
    x, y, z : floats, scalar or array-like
      The coordinates of vector corresponding to input pixels. Scalar if all input
      are scalar, array otherwise. Usual numpy broadcasting rules apply.

    See Also
    --------
    ang2pix, pix2ang, vec2pix

    Examples
    --------
    >>> import healpy as hpy
    >>> hpy.pix2vec(16, 1504)
    (0.99879545620517241, 0.049067674327418015, 0.0)

    >>> hpy.pix2vec(16, [1440,  427])
    (array([ 0.99913157,  0.5000534 ]), array([ 0.       ,  0.5000534]), array([ 0.04166667,  0.70703125]))

    >>> hpy.pix2vec([1, 2], 11)
    (array([ 0.52704628,  0.68861915]), array([-0.52704628, -0.28523539]), array([-0.66666667,  0.66666667]))
    """
    if nest:
        return pixlib._pix2vec_nest(nside,ipix)
    else:
        return pixlib._pix2vec_ring(nside,ipix)

def ang2vec(theta, phi):
    """ang2vec : convert angles to 3D position vector

    Parameters
    ----------
    theta : float, scalar or arry-like
      colatitude in radians measured southward from north pole (in [0,pi]). 
    phi : float, scalar or array-like
      longitude in radians measured eastward (in [0, 2*pi]). 

    Returns
    -------
    vec : float, array
      if theta and phi are vectors, the result is a 2D array with a vector per row
      otherwise, it is a 1D array of shape (3,)

    See Also
    --------
    vec2ang, rotator.dir2vec, rotator.vec2dir
    """
    if npy.any(theta < 0) or npy.any(theta > npy.pi):
        raise exceptions.ValueError('THETA is out of range [0,pi]')
    sintheta = npy.sin(theta)
    return npy.array([sintheta*npy.cos(phi),
                      sintheta*npy.sin(phi),
                      npy.cos(theta)]).T

def vec2ang(vectors):
    """vec2ang: vectors [x, y, z] -> theta[rad], phi[rad]

    Parameters
    ----------
    vectors : float, array-like
      the vector(s) to convert, shape is (3,) or (N, 3)

    Returns
    -------
    theta, phi : float, tuple of two arrays
      the colatitude and longitude in radians

    See Also
    --------
    ang2vec, rotator.vec2dir, rotator.dir2vec
    """
    vectors = vectors.reshape(-1,3)
    dnorm = npy.sqrt(npy.sum(npy.square(vectors),axis=1))
    theta = npy.arccos(vectors[:,2]/dnorm)
    phi = npy.arctan2(vectors[:,1],vectors[:,0])
    phi[phi < 0] += 2*npy.pi
    return theta, phi

def ring2nest(nside, ipix):
    """Convert pixel number from RING ordering to NESTED ordering.

    Parameters
    ----------
    nside : int, scalar or array-like
      the healpix nside parameter
    ipix : int, scalar or array-like
      the pixel number in RING scheme

    Returns
    -------
    ipix : int, scalar or array-like
      the pixel number in NESTED scheme

    See Also
    --------
    nest2ring, reorder
    
    Examples
    --------
    >>> import healpy as hpy
    >>> hpy.ring2nest(16, 1504)
    1130

    >>> hpy.ring2nest(2, range(10))
    array([ 3,  7, 11, 15,  2,  1,  6,  5, 10,  9])
    
    >>> hpy.ring2nest([1, 2, 4, 8], 11)
    array([ 11,  13,  61, 253])
    """
    return pixlib._ring2nest(nside, ipix)

def nest2ring(nside, ipix):
    """Convert pixel number from NESTED ordering to RING ordering.

    Parameters
    ----------
    nside : int, scalar or array-like
      the healpix nside parameter
    ipix : int, scalar or array-like
      the pixel number in NESTED scheme

    Returns
    -------
    ipix : int, scalar or array-like
      the pixel number in RING scheme

    See Also
    --------
    ring2nest, reorder
    
    Examples
    --------
    >>> import healpy as hpy
    >>> hpy.nest2ring(16, 1130)
    1504

    >>> hpy.nest2ring(2, range(10))
    array([13,  5,  4,  0, 15,  7,  6,  1, 17,  9])
    
    >>> hpy.nest2ring([1, 2, 4, 8], 11)
    array([ 11,   2,  12, 211])
    """
    return pixlib._nest2ring(nside, ipix)

def reorder(map_in, inp=None, out=None, r2n=None, n2r=None):
    """Reorder an healpix map from RING/NESTED ordering to NESTED/RING

    Parameters
    ----------
    map_in : array-like
      the input map to reorder
    inp, out : ``'RING'`` or ``'NESTED'``
      define the input and output ordering
    r2n : bool
      if True, reorder from RING to NESTED
    n2r : bool
      if True, reorder from NESTED to RING

    Returns
    -------
    map_out : array-like
      the reordered map

    Notes
    -----
    if ``r2n`` or ``n2r`` is defined, override ``inp`` and ``out``.

    See Also
    --------
    nest2ring, ring2nest

    Examples
    --------
    >>> import healpy as hpy
    >>> hpy.reorder(npy.arange(48), r2n = True)
    array([13,  5,  4,  0, 15,  7,  6,  1, 17,  9,  8,  2, 19, 11, 10,  3, 28,
           20, 27, 12, 30, 22, 21, 14, 32, 24, 23, 16, 34, 26, 25, 18, 44, 37,
           36, 29, 45, 39, 38, 31, 46, 41, 40, 33, 47, 43, 42, 35])
    >>> hpy.reorder(range(12), n2r = True)
    array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11])
    """
    typ = maptype(map_in)
    if typ < 0:
        raise TypeError('map_in is not a map nor a sequence of maps')
    if typ == 0:
        npix = len(map_in)
    else:
        npix = len(map_in[0])
    nside = npix2nside(npix)
    if nside>128:
        bunchsize = npix/24
    else:
        bunchsize = npix
    if r2n:
        inp='RING'
        out='NEST'
    if n2r:
        inp='NEST'
        out='RING'
    inp = str(inp).upper()[0:4]
    out = str(out).upper()[0:4]
    if inp not in ['RING','NEST'] or out not in ['RING','NEST']:
        raise ValueError('inp and out must be either RING or NEST')
    if typ == 0:
        mapin = [map_in]
    else:
        mapin = map_in
    mapout = []
    for m_in in mapin:
        if inp == out:
            mapout.append(m_in)
        elif inp == 'RING':
            m_out = npy.zeros(npix,dtype=type(m_in[0]))
            for ibunch in range(npix/bunchsize):
                ipix_n = npy.arange(ibunch*bunchsize,
                                    (ibunch+1)*bunchsize)
                ipix_r = nest2ring(nside, ipix_n)
                m_out[ipix_n] = npy.asarray(m_in)[ipix_r]
            mapout.append(m_out)
        elif inp == 'NEST':
            m_out = npy.zeros(npix,dtype=type(m_in[0]))
            for ibunch in range(npix/bunchsize):
                ipix_r = npy.arange(ibunch*bunchsize,
                                    (ibunch+1)*bunchsize)
                ipix_n = ring2nest(nside, ipix_r)
                m_out[ipix_r] = npy.asarray(m_in)[ipix_n]
            mapout.append(m_out)
    if typ == 0:
        return mapout[0]
    else:
        return mapout

def nside2npix(nside):
    """Give the number of pixel for the given nside.

    Parameters
    ----------
    nside : int
      healpix nside parameter; an exception is raised if nside is not valid
      (nside must be a power of 2)

    Returns
    -------
    npix : int
      corresponding number of pixels
    
    Notes
    -----
    Raise a ValueError exception if nside is not valid.

    Examples
    --------
    >>> import healpy as hpy
    >>> hpy.nside2npix(8)
    768

    >>> npy.all([hpy.nside2npix(nside) == 12 * nside**2 for nside in [2**n for n in range(12)]])
    True

    >>> hpy.nside2npix(7)
    Traceback (most recent call last):
       ...
    ValueError: Given number is not a valid nside parameter (must be a power of 2)
    """
    if not isnsideok(nside):
        raise ValueError("Given number is not a valid nside parameter "
                         "(must be a power of 2)")
    return 12*nside**2

def nside2resol(nside, arcmin=False):
    """Give approximate resolution for nside.

    Resolution is just the square root of the pixel area, which is a gross
    approximation given the different pixel shapes

    Parameters
    ----------
    nside : int
      healpix nside parameter, must be a power of 2
    arcmin : bool
      if True, return resolution in arcmin, otherwise in radian

    Returns
    -------
    resol : float
      approximate pixel size in radians or arcmin

    Notes
    -----
    Raise a ValueError exception if nside is not valid.

    Examples
    --------
    >>> import healpy as hpy
    >>> hpy.nside2resol(128, arcmin = True)
    27.483891294539248

    >>> hpy.nside2resol(256)
    0.0039973699529159707

    >>> hpy.nside2resol(7)
    Traceback (most recent call last):
       ...
    ValueError: Given number is not a valid nside parameter (must be a power of 2)
    """
    if not isnsideok(nside):
        raise ValueError("Given number is not a valid nside parameter "
                         "(must be a power of 2)")
    
    resol = npy.sqrt(nside2pixarea(nside))

    if arcmin:
        resol = npy.rad2deg(resol) * 60
        
    return resol


def nside2pixarea(nside, degrees=False):
    """Give pixel area given nside.

    Parameters
    ----------
    nside : int
      healpix nside parameter, must be a power of 2
    degrees : bool
      if True, returns pixel area in square degrees, in square radians otherwise

    Returns
    -------
    pixarea : float
      pixel area in suqare radian or square degree

    Notes
    -----
    Raise a ValueError exception if nside is not valid.

    Examples
    --------
    >>> import healpy as hpy
    >>> hpy.nside2pixarea(128, degrees = True)
    0.2098234113027917

    >>> hpy.nside2pixarea(256)
    1.5978966540475428e-05

    >>> hpy.nside2pixarea(7)
    Traceback (most recent call last):
       ...
    ValueError: Given number is not a valid nside parameter (must be a power of 2)
    """
    if not isnsideok(nside):
        raise ValueError("Given number is not a valid nside parameter "
                         "(must be a power of 2)")
    
    pixarea = 4*npy.pi/nside2npix(nside)

    if degrees:
        pixarea = npy.rad2deg(npy.rad2deg(pixarea))
        
    return pixarea

def npix2nside(npix):
    """Give the nside parameter for the given number of pixels.

    Parameters
    ----------
    npix : int
      the number of pixels
    
    Returns
    -------
    nside : int
      the nside parameter corresponding to npix

    Notes
    -----
    Raise a ValueError exception if number of pixel does not correspond to
    the number of pixel of an healpix map.

    Examples
    --------
    >>> import healpy as hpy
    >>> hpy.npix2nside(768)
    8

    >>> npy.all([hpy.npix2nside(12 * nside**2) == nside for nside in [2**n for n in range(12)]])
    True

    >>> hpy.npix2nside(1000)
    Traceback (most recent call last):
        ...
    ValueError: Wrong pixel number (it is not 12*nside**2)
    """
    nside = npy.sqrt(npix/12.)
    if nside != npy.floor(nside):
        raise ValueError("Wrong pixel number (it is not 12*nside**2)")
    nside=int(npy.floor(nside))
    if not isnsideok(nside):
        raise ValueError("Wrong nside value (it is not 2**N)")
    return nside

def isnsideok(nside):
    """Returns :const:`True` if nside is a valid nside parameter, :const:`False` otherwise.

    Parameters
    ----------
    nside : int, scalar or array-like
      integer value to be tested

    Returns
    -------
    ok : bool, scalar or array-like
      :const:`True` if given value is a valid nside, :const:`False` otherwise.

    Examples
    --------
    >>> import healpy as hpy
    >>> hpy.isnsideok(13)
    False
    
    >>> hpy.isnsideok(32)
    True

    >>> hpy.isnsideok([1, 2, 3, 4, 8, 16])
    array([ True,  True, False,  True,  True,  True], dtype=bool)
    """
    if hasattr(nside, '__len__'):
        return nside == 2**npy.int32(npy.around(npy.ma.log2(nside).filled(0)))
    elif nside <= 0:
        return False
    else:
        return nside == 2**int(round(npy.log2(nside)))

def isnpixok(npix):
    """Return :const:`True` if npix is a valid value for healpix map size, :const:`False` otherwise.

    Parameters
    ----------
    npix : int, scalar or array-like
      integer value to be tested

    Returns
    -------
    ok : bool, scalar or array-like
      :const:`True` if given value is a valid number of pixel, :const:`False` otherwise

    Examples
    --------
    >>> import healpy as hpy
    >>> hpy.isnpixok(12)
    True
    
    >>> hpy.isnpixok(768)
    True

    >>> hpy.isnpixok([12, 768, 1002])
    array([ True,  True, False], dtype=bool)
    """
    if hasattr(npix,'__len__'):
        nside = npy.sqrt(npy.asarray(npix)/12.)
        return isnsideok(nside)
    else:
        nside = npy.sqrt(npix/12.)
        return isnsideok(nside)

def get_interp_val(m,theta,phi,nest=False):
    """Return the bi-linear interpolation value of a map using 4 nearest neighbours.

    Parameters
    ----------
    m : array-like
      an healpix map
    theta, phi : float, scalar or array-like
      angular coordinates of point at which to interpolate the map
    nest : bool
      if True, the is assumed to be in NESTED ordering.

    Returns
    -------
      val : float, scalar or arry-like
        the interpolated value(s), usual numpy broadcasting rules apply.

    See Also
    --------
    get_neighbours, get_all_neighbours

    Examples
    --------
    >>> import healpy as hpy
    >>> hpy.get_interp_val(npy.arange(12.), npy.pi/2, 0)
    4.0
    >>> hpy.get_interp_val(npy.arange(12.), npy.linspace(0, npy.pi, 10), 0)
    array([ 1.5       ,  1.5       ,  1.5       ,  2.20618428,  3.40206143,
            5.31546486,  7.94639458,  9.5       ,  9.5       ,  9.5       ])
    """
    m2=m.ravel()
    nside=npix2nside(m2.size)
    if nest:
        r=pixlib._get_interpol_nest(nside,theta,phi)
    else:
        r=pixlib._get_interpol_ring(nside,theta,phi)
    p=npy.array(r[0:4])
    w=npy.array(r[4:8])
    del r
    return npy.sum(m2[p]*w,0)

def get_neighbours(nside,theta,phi=None,nest=False):
    """Return the 4 nearest pixels and corresponding weights.

    Parameters
    ----------
    nside : int
      the healpix nside
    theta, phi : float, scalar or array-like
      if phi is not given, theta is interpreted as pixel number,
      otherwise theta[rad],phi[rad] are angular coordinates
    nest : bool
      if ``True``, NESTED ordering, otherwise RING ordering.

    Returns
    -------
    res : tuple of length 2
      contains pixel numbers in res[0] and weights in res[1].
      Usual numpy broadcasting rules apply.

    See Also
    --------
    get_interp_val, get_all_neighbours

    Examples
    --------
    >>> import healpy as hpy
    >>> hpy.get_neighbours(1, 0)
    (array([0, 1, 4, 5]), array([ 1.,  0.,  0.,  0.]))

    >>> hpy.get_neighbours(1, 0, 0)
    (array([1, 2, 3, 0]), array([ 0.25,  0.25,  0.25,  0.25]))

    >>> hpy.get_neighbours(1, [0, npy.pi/2], 0)
    (array([[ 1,  4],
           [ 2,  5],
           [ 3, 11],
           [ 0,  8]]), array([[ 0.25,  1.  ],
           [ 0.25,  0.  ],
           [ 0.25,  0.  ],
           [ 0.25,  0.  ]]))
    """
    if not isnsideok(nside):
        raise ValueError('Wrong nside value. Must be a power of 2.')
    if phi == None:
        theta,phi = pix2ang(nside,theta,nest=nest)
    if nest:
        r=pixlib._get_interpol_nest(nside,theta,phi)
    else:
        r=pixlib._get_interpol_ring(nside,theta,phi)
    p=npy.array(r[0:4])
    w=npy.array(r[4:8])
    return (p,w)

def get_all_neighbours(nside, theta, phi=None, nest=False):
    """Return the 8 nearest pixels.

    Parameters
    ----------
    nside : int
      the nside to work with
    theta, phi : scalar or array-like
      if phi is not given or None, theta is interpreted as pixel number,
      otherwise, theta[rad],phi[rad] are angular coordinates
    nest : bool
      if ``True``, pixel number will be NESTED ordering, otherwise RING ordering.

    Returns
    -------
    ipix : int, array
      pixel number of the SW, W, NW, N, NE, E, SE and S neighbours,
      shape is (8,) if input is scalar, otherwise shape is (8, N) if input is
      of length N. If a neighbor does not exist (it can be the case for W, N, E and S)
      the corresponding pixel number will be -1.

    See Also
    --------
    get_neighbours, get_interp_val

    Examples
    --------
    >>> import healpy as hpy
    >>> hpy.get_all_neighbours(1, 4)
    array([11,  7,  3, -1,  0,  5,  8, -1])

    >>> hpy.get_all_neighbours(1, npy.pi/2, npy.pi/2)
    array([ 8,  4,  0, -1,  1,  6,  9, -1])
    """
    if not isnsideok(nside):
        raise ValueError('Wrong nside value. Must be a power of 2.')
    if phi is not None:
        theta = ang2pix(nside,theta, phi,nest=nest)
    if nest:
        r=pixlib._get_neighbors_nest(nside,theta)
    else:
        r=pixlib._get_neighbors_ring(nside,theta)
    res=npy.array(r[0:8])
    return res

def fit_dipole(m, nest=False, bad=UNSEEN, gal_cut=0):
    """Fit a dipole and a monopole to the map, excluding bad pixels.

    Parameters
    ----------
    m : float, array-like
      the map to which a dipole is fitted and subtracted
    nest : bool
      if ``False`` m is assumed in RING scheme, otherwise map is NESTED
    bad : float
      bad values of pixel, default to :const:`UNSEEN`.
    gal_cut : float
      pixels at latitude in [-gal_cut;+gal_cut] degrees are not taken into account

    Returns
    -------
    res : tuple of length 2
      the monopole value in res[0] and the dipole vector (as array) in res[1]

    See Also
    --------
    remove_dipole, fit_monopole, remove_monopole
    """
    m=npy.asarray(m)
    npix = m.size
    nside = npix2nside(npix)
    if nside>128:
        bunchsize = npix/24
    else:
        bunchsize = npix
    aa = npy.zeros((4,4),dtype=npy.float64)
    v = npy.zeros(4,dtype=npy.float64)
    for ibunch in range(npix/bunchsize):
        ipix = npy.arange(ibunch*bunchsize,
                          (ibunch+1)*bunchsize)
        ipix = ipix[(m.flat[ipix]!=bad) & (npy.isfinite(m.flat[ipix]))]
        x,y,z = pix2vec(nside, ipix, nest)
        if gal_cut>0:
            w = (npy.abs(z)>=npy.sin(gal_cut*npy.pi/180))
            ipix=ipix[w]
            x=x[w]
            y=y[w]
            z=z[w]
            del w
        aa[0,0] += ipix.size
        aa[1,0] += x.sum()
        aa[2,0] += y.sum()
        aa[3,0] += z.sum()
        aa[1,1] += (x**2).sum()
        aa[2,1] += (x*y).sum()
        aa[3,1] += (x*z).sum()
        aa[2,2] += (y**2).sum()
        aa[3,2] += (y*z).sum()
        aa[3,3] += (z**2).sum()
        v[0] += m.flat[ipix].sum()
        v[1] += (m.flat[ipix]*x).sum()
        v[2] += (m.flat[ipix]*y).sum()
        v[3] += (m.flat[ipix]*z).sum()
    aa[0,1] = aa[1,0]
    aa[0,2] = aa[2,0]
    aa[0,3] = aa[3,0]
    aa[1,2] = aa[2,1]
    aa[1,3] = aa[3,1]
    aa[2,3] = aa[3,2]
    res = npy.dot(npy.linalg.inv(aa),v)
    mono = res[0]
    dipole = res[1:4]
    return mono,dipole

def remove_dipole(m,nest=False,bad=UNSEEN,gal_cut=0,fitval=False,
                  copy=True,verbose=False):
    """Fit and subtract the dipole and the monopole from the given map m.

    Parameters
    ----------
    m : float, array-like
      the map to which a dipole is fitted and subtracted
    nest : bool
      if ``False`` m is assumed in RING scheme, otherwise map is NESTED
    bad : float
      bad values of pixel, default to :const:`UNSEEN`.
    gal_cut : float
      pixels at latitude in [-gal_cut;+gal_cut] are not taken into account
    fitval : bool
      whether to return or not the fitted values of monopole and dipole
    copy : bool
      whether to modify input map or not (by default, make a copy)
    verbose : bool
      print values of monopole and dipole

    Returns
    -------
    res : array or tuple of length 3
      if fitval is False, returns map with monopole and dipole subtracted,
      otherwise, returns map (array, in res[0]), monopole (float, in res[1]), 
      dipole_vector (array, in res[2])

    See Also
    --------
    fit_dipole, fit_monopole, remove_monopole
    """
    m=npy.array(m,copy=copy)
    npix = m.size
    nside = npix2nside(npix)
    if nside>128:
        bunchsize = npix/24
    else:
        bunchsize = npix
    mono,dipole = fit_dipole(m,nest=nest,bad=bad,gal_cut=gal_cut)
    for ibunch in range(npix/bunchsize):
        ipix = npy.arange(ibunch*bunchsize,
                          (ibunch+1)*bunchsize)
        ipix = ipix[(m.flat[ipix]!=bad) & (npy.isfinite(m.flat[ipix]))]
        x,y,z = pix2vec(nside, ipix, nest)
        m.flat[ipix] -= (dipole[0]*x)
        m.flat[ipix] -= dipole[1]*y
        m.flat[ipix] -= dipole[2]*z
        m.flat[ipix] -= mono
    if verbose:
        import rotator as R
        lon,lat = R.vec2dir(dipole,lonlat=True)
        amp = npy.sqrt((dipole**2).sum())
        print 'monopole: %g  dipole: lon: %g, lat: %g, amp: %g'%(mono,
                                                                 lon,
                                                                 lat,
                                                                 amp)
    if fitval:
        return m,mono,dipole
    else:
        return m

def fit_monopole(m,nest=False,bad=pixlib.UNSEEN,gal_cut=0):
    """Fit a monopole to the map, excluding unseen pixels.

    Parameters
    ----------
    m : float, array-like
      the map to which a dipole is fitted and subtracted
    nest : bool
      if ``False`` m is assumed in RING scheme, otherwise map is NESTED
    bad : float
      bad values of pixel, default to :const:`UNSEEN`.
    gal_cut : float
      pixels at latitude in [-gal_cut;+gal_cut] degrees are not taken into account

    Returns
    -------
    res: float
      fitted monopole value

    See Also
    --------
    fit_dipole, remove_monopole, remove_monopole
    """
    m=npy.asarray(m)
    npix=m.size
    nside = npix2nside(npix)
    if nside>128:
        bunchsize=npix/24
    else:
        bunchsize=npix
    aa = v = 0.0
    for ibunch in range(npix/bunchsize):
        ipix = npy.arange(ibunch*bunchsize,
                          (ibunch+1)*bunchsize)
        ipix = ipix[(m.flat[ipix]!=bad) & (npy.isfinite(m.flat[ipix]))]
        x,y,z = pix2vec(nside, ipix, nest)
        if gal_cut>0:
            w = (npy.abs(z)>=npy.sin(gal_cut*npy.pi/180))
            ipix=ipix[w]
            x=x[w]
            y=y[w]
            z=z[w]
            del w
        aa += ipix.size
        v += m.flat[ipix].sum()
    mono = v/aa
    return mono

def remove_monopole(m,nest=False,bad=pixlib.UNSEEN,gal_cut=0,fitval=False,
                    copy=True,verbose=False):
    """Fit and subtract the monopole from the given map m.

    Parameters
    ----------
    m : float, array-like
      the map to which a monopole is fitted and subtracted
    nest : bool
      if ``False`` m is assumed in RING scheme, otherwise map is NESTED
    bad : float
      bad values of pixel, default to :const:`UNSEEN`.
    gal_cut : float
      pixels at latitude in [-gal_cut;+gal_cut] are not taken into account
    fitval : bool
      whether to return or not the fitted value of monopole
    copy : bool
      whether to modify input map or not (by default, make a copy)
    verbose: bool
      whether to print values of monopole

    Returns
    -------
    res : array or tuple of length 3
      if fitval is False, returns map with monopole subtracted,
      otherwise, returns map (array, in res[0]) and monopole (float, in res[1])

    See Also
    --------
    fit_dipole, fit_monopole, remove_dipole
    """
    m=npy.array(m,copy=copy)
    npix = m.size
    nside = npix2nside(npix)
    if nside>128:
        bunchsize = npix/24
    else:
        bunchsize = npix
    mono = fit_monopole(m,nest=nest,bad=bad,gal_cut=gal_cut)
    for ibunch in range(npix/bunchsize):
        ipix = npy.arange(ibunch*bunchsize,
                          (ibunch+1)*bunchsize)
        ipix = ipix[(m.flat[ipix]!=bad) & (npy.isfinite(m.flat[ipix]))]
        x,y,z = pix2vec(nside, ipix, nest)
        m.flat[ipix] -= mono
    if verbose:
        print 'monopole: %g'%mono
    if fitval:
        return m,mono
    else:
        return m

def get_map_size(m):
    """Returns the npix of a given map (implicit or explicit pixelization).

     If map is a dict type, assumes explicit pixelization: use nside key if present, or use 
     nside attribute if present, otherwise use the smallest valid npix given the maximum key value.
     otherwise assumes implicit pixelization and returns len(m).

     Parameters
     ----------
     m : array-like or dict-like
       a map with implicit (array-like) or explicit (dict-like) pixellization

     Returns
     -------
     npix : int
       a valid number of pixel

     Notes
     -----
     In implicit pixellization, raise a ValueError exception if the size of the input
     is not a valid pixel number.

     Examples
     --------
    >>> import healpy as hpy
     >>> m = {0: 1, 1: 1, 2: 1, 'nside': 1}
     >>> print hpy.get_map_size(m)
     12

     >>> m = {0: 1, 767: 1}
     >>> print hpy.get_map_size(m)
     768

     >>> print hpy.get_map_size(npy.zeros(12 * 8 ** 2))
     768
    """
    if isinstance(m, dict):
        if 'nside' in m:
            return nside2npix(m['nside'])
        elif hasattr(ma, 'nside'):
            return nside2npix(m.nside)
        else:
            nside = get_min_valid_nside(max(m.keys())+1)
            return nside2npix(nside)
    else:
        if isnpixok(len(m)):
            return len(m)
        else:
            raise ValueError("Wrong pixel number (it is not 12*nside**2)")

def get_min_valid_nside(npix):
    """Returns the minimum acceptable nside so that npix <= nside2npix(nside).

    Parameters
    ----------
    npix : int
      a minimal number of pixel

    Returns
    -------
    nside : int
      a valid healpix nside so that 12 * nside ** 2 >= npix

    Examples
    --------
    >>> import healpy as hpy
    >>> hpy.pixelfunc.get_min_valid_nside(355)
    8
    >>> hpy.pixelfunc.get_min_valid_nside(768)
    8
    """
    order = 0.5 * npy.log2(npix / 12.)
    return 2**int(npy.ceil(order))

def maptype(m):
    """Describe the type of the map (valid, single, sequence of maps).

    Parameters
    ----------
    m : sequence
      the map to get info from

    Returns
    -------
    info : int
      Returns -1 if the given object is not a valid map.
      Returns 0 if it is a map.
      Returns info>0 if it is a sequence of maps (info: number of maps in the sequence)

    Examples
    --------
    >>> import healpy as hpy
    >>> hpy.pixelfunc.maptype(npy.arange(12))
    0
    >>> hpy.pixelfunc.maptype(2)
    -1
    >>> hpy.pixelfunc.maptype([npy.arange(12), npy.arange(12)])
    2
    >>> hpy.pixelfunc.maptype([npy.arange(12), npy.arange(768)])
    -1
    """
    if not hasattr(m, '__len__'):
        return -1
    if len(m) == 0:
        return -1
    if hasattr(m[0], '__len__'):
        npix=len(m[0])
        for mm in m[1:]:
            if len(mm) != npix:
                return -1
        if isnpixok(len(m[0])):
            return len(m)
        else:
            return -1
    else:
        if isnpixok(len(m)):
            return 0
        else:
            return -1

def get_nside(m):
    """Return the nside of the given map.

    Parameters
    ----------
    m : sequence
      the map to get the nside from.

    Returns
    -------
    nside : int
      the healpix nside parameter of the map (or sequence of maps)

    Notes
    -----
    If the input is a sequence of maps, all of them must have same size.
    If the input is not a valid map (not a sequence, unvalid number of pixels),
    a TypeError exception is raised.
    """
    typ = maptype(m)
    if typ < 0:
        raise TypeError('m is not a map nor a sequence of maps of same size')
    if typ == 0:
        return npix2nside(len(m))
    else:
        return npix2nside(len(m[0]))

def ud_grade(map_in,nside_out,pess=False,order_in='RING',order_out=None,
             power=None, dtype=None):
    """Upgrade or degrade resolution of a map (or list of maps).

    Parameters
    ----------
    map_in : array-like or sequence of array-like
      the input map(s) (if a sequence of maps, all must have same size)
    nside_out : int
      the desired nside of the output map(s)
    pess : bool
      if ``True``, in degrading, reject pixels which contains
      a bad sub_pixel. Otherwise, estimate average with good pixels
    order_in, order_out : str
      pixel ordering of input and output ('RING' or 'NESTED')
    power : float
      if non-zero, multiply the result by (nside_in/nside_out)**power
      For example, power=-2 keep the sum of the map invariant
    dtype : type
      the type of the output map

    Returns
    -------
    map_out : array-like or sequence of array-like
      the upgraded or degraded map(s)

    Examples
    --------
    >>> import healpy as hpy
    >>> hpy.ud_grade(npy.arange(48.), 1)
    array([  5.5 ,   7.25,   9.  ,  10.75,  21.75,  21.75,  23.75,  25.75,
            36.5 ,  38.25,  40.  ,  41.75])
    """
    if not isnsideok(nside_out):
        raise ValueError('Invalid nside for output')
    typ = maptype(map_in)
    if typ<0:
        raise TypeError('Invalid map')
    if typ == 0:
        m_in = [map_in]
    else:
        m_in = map_in
    mapout = []
    if order_out is None: order_out = order_in
    for m in m_in:
        if str(order_in).upper()[0:4] == 'RING':
            m = reorder(m,r2n=True)
        mout = _ud_grade_core(m,nside_out,pess=pess, power=power, dtype=dtype)
        if str(order_out).upper()[0:4] == 'RING':
            mout = reorder(mout,n2r=True)
        mapout.append(mout)
    if typ == 0:
        return mapout[0]
    else:
        return mapout

def _ud_grade_core(m,nside_out,pess=False,power=None, dtype=None):
    """Internal routine used by ud_grade. It assumes that the map is NESTED
    and single (not a list of maps)
    """
    nside_in = get_nside(m)
    if dtype:
        type_out = dtype
    else:
        type_out = type(m[0])
    if not isnsideok(nside_out):
        raise ValueError('invalid nside_out value')
    npix_in = nside2npix(nside_in)
    npix_out = nside2npix(nside_out)

    if power:
        power = float(power)
        ratio = (float(nside_out)/float(nside_in))**power
    else:
        ratio = 1
    
    if nside_out > nside_in:
        rat2 = npix_out/npix_in
        fact = npy.ones(rat2, dtype=type_out)*ratio
        map_out = npy.outer(m,fact).reshape(npix_out)
    elif nside_out < nside_in:
        rat2 = npix_in/npix_out
        bads = (mask_bad(m) | (~npy.isfinite(m)))
        hit = npy.ones(npix_in,dtype=npy.int16)
        hit[bads] = 0
        m[bads] = 0
        mr = m.reshape(npix_out,rat2)
        hit = hit.reshape(npix_out,rat2)
        map_out = mr.sum(axis=1).astype(type_out)
        nhit = hit.sum(axis=1)
        if pess:
            badout = npy.where(nhit != rat2)
        else:
            badout = npy.where(nhit == 0)
        if power:
            nhit /= ratio
        map_out /= nhit
        try:
            map_out[badout] = UNSEEN
            m[bads] = UNSEEN
        except OverflowError:
            pass
    else:
        map_out = m
    return map_out.astype(type_out)

