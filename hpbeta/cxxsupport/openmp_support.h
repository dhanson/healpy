/*
 *  This file is part of libcxxsupport.
 *
 *  libcxxsupport is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  libcxxsupport is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with libcxxsupport; if not, write to the Free Software
 *  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

/*
 *  libcxxsupport is being developed at the Max-Planck-Institut fuer Astrophysik
 *  and financially supported by the Deutsches Zentrum fuer Luft- und Raumfahrt
 *  (DLR).
 */

/*
 *  Copyright (C) 2005-2011 Max-Planck-Society
 *  \author Martin Reinecke
 */

#ifndef PLANCK_OPENMP_SUPPORT_H
#define PLANCK_OPENMP_SUPPORT_H

#ifdef _OPENMP
#include <omp.h>
#endif

#include "share_utils.h"

inline bool openmp_enabled()
  {
#ifdef _OPENMP
  return true;
#else
  return false;
#endif
  }

inline int openmp_max_threads ()
  {
#ifdef _OPENMP
  return omp_get_max_threads();
#else
  return 1;
#endif
  }

inline int openmp_num_threads ()
  {
#ifdef _OPENMP
  return omp_get_num_threads();
#else
  return 1;
#endif
  }

inline int openmp_thread_num ()
  {
#ifdef _OPENMP
  return omp_get_thread_num();
#else
  return 0;
#endif
  }

/*! Calculates the range of indices between \a glo and \a ghi which
    must be processed by this thread and returns it in \a lo and \a hi.

    The indices \a ghi and \a hi are "one past the last real index",
    in analogy to the STL iterators. */
inline void openmp_calc_share (int64 glo, int64 ghi, int64 &lo, int64 &hi)
  {
#ifdef _OPENMP
  calcShareGeneral (glo,ghi,omp_get_num_threads(),omp_get_thread_num(),lo,hi);
#else
  lo=glo; hi=ghi;
#endif
  }

#endif
