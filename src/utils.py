"""
📝 'iMarker Detector (Standalone)' Software
    SPDX-FileCopyrightText: (2025) University of Luxembourg
    © 2025 University of Luxembourg
    Developed by: Ali TOURANI et al. at SnT / ARG.

'iMarker Detector (Standalone)' is licensed under the "SNT NON-COMMERCIAL" License.
You may not use this file except in compliance with the License.
"""

import io
import pstats
import cProfile


def startProfiler():
    # Profile the code
    profile = cProfile.Profile()
    profile.enable()
    return profile


def stopProfiler(profile):
    print("\nProfiler results:")
    # Stop the profiler
    profile.disable()
    str = io.StringIO()
    stats = pstats.Stats(profile, stream=str).sort_stats(
        pstats.SortKey.TIME)
    stats.print_stats(35)
    print(str.getvalue())
