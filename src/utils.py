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
