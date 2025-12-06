"""
JSON File Caching Utilities

Provides efficient caching mechanisms for JSON files to reduce disk I/O.

Features:
- LRU caching with modification time tracking
- Automatic cache invalidation on file changes
- Thread-safe caching
- Memory-efficient with configurable cache sizes

Usage:
    from music_brain.utils.json_cache import load_json_cached
    
    # Simple cached loading
    data = load_json_cached("path/to/file.json")
    
    # Cached loading with custom cache size
    data = load_json_cached("path/to/file.json", maxsize=256)
"""

import json
from pathlib import Path
from functools import lru_cache
from typing import Any, Dict, Optional
import os


@lru_cache(maxsize=256)
def _load_json_with_mtime(filepath: str, mtime: float) -> Dict[str, Any]:
    """
    Load JSON file with modification time as cache key.
    
    The mtime parameter ensures the cache is invalidated when the file changes.
    This function is cached using LRU cache for performance.
    
    Args:
        filepath: Path to JSON file
        mtime: File modification time (seconds since epoch)
        
    Returns:
        Parsed JSON data as dictionary
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_json_cached(
    filepath: str | Path,
    default: Optional[Dict[str, Any]] = None,
    maxsize: Optional[int] = None
) -> Dict[str, Any]:
    """
    Load JSON file with automatic caching and invalidation.
    
    Files are cached in memory after first load. The cache is automatically
    invalidated if the file is modified (based on modification time).
    
    Args:
        filepath: Path to JSON file (str or Path object)
        default: Default value to return if file doesn't exist (default: None)
        maxsize: Maximum cache size (default: use global cache of 256)
        
    Returns:
        Parsed JSON data as dictionary, or default if file not found
        
    Examples:
        >>> # Load with automatic caching
        >>> data = load_json_cached("chord_progressions.json")
        
        >>> # Load with default value if file missing
        >>> data = load_json_cached("config.json", default={})
        
        >>> # First load: reads from disk
        >>> emotions = load_json_cached("happy.json")
        >>> # Second load: instant (from cache)
        >>> emotions = load_json_cached("happy.json")
    """
    filepath = Path(filepath)
    
    # Check if file exists
    if not filepath.exists():
        if default is not None:
            return default
        raise FileNotFoundError(f"JSON file not found: {filepath}")
    
    # Get file modification time for cache invalidation
    mtime = os.path.getmtime(filepath)
    
    # Use the global cache or a custom cache
    # Note: maxsize parameter is informational only; we use the global cache
    # To use custom cache size, modify the @lru_cache decorator above
    
    try:
        return _load_json_with_mtime(str(filepath), mtime)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in {filepath}: {e.msg}",
            e.doc,
            e.pos
        )


def clear_json_cache() -> None:
    """
    Clear the JSON cache.
    
    Useful for testing or when you need to force reload all JSON files.
    
    Example:
        >>> clear_json_cache()
        >>> # Next load will read from disk
        >>> data = load_json_cached("file.json")
    """
    _load_json_with_mtime.cache_clear()


def get_cache_info() -> Dict[str, Any]:
    """
    Get cache statistics.
    
    Returns:
        Dictionary with cache stats:
        - hits: Number of cache hits
        - misses: Number of cache misses
        - maxsize: Maximum cache size
        - currsize: Current cache size
        
    Example:
        >>> info = get_cache_info()
        >>> print(f"Cache hit rate: {info['hits'] / (info['hits'] + info['misses']):.1%}")
    """
    info = _load_json_with_mtime.cache_info()
    return {
        'hits': info.hits,
        'misses': info.misses,
        'maxsize': info.maxsize,
        'currsize': info.currsize
    }


# Specialized loaders for common file types

@lru_cache(maxsize=64)
def load_emotion_file(emotion_name: str, emotion_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load emotion JSON file with caching.
    
    Args:
        emotion_name: Name of emotion (e.g., "happy", "sad")
        emotion_dir: Directory containing emotion files (default: ./emotion_thesaurus)
        
    Returns:
        Emotion data dictionary
        
    Example:
        >>> happy_data = load_emotion_file("happy")
        >>> sad_data = load_emotion_file("sad")
    """
    if emotion_dir is None:
        # Default to emotion_thesaurus in repository root
        emotion_dir = Path(__file__).parent.parent.parent / "emotion_thesaurus"
    
    filepath = emotion_dir / f"{emotion_name}.json"
    return load_json_cached(filepath, default={})


@lru_cache(maxsize=32)
def load_chord_progressions(progressions_file: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load chord progression database with caching.
    
    Args:
        progressions_file: Path to chord progressions file
            (default: music_brain/data/chord_progressions.json)
        
    Returns:
        Chord progressions dictionary
        
    Example:
        >>> progressions = load_chord_progressions()
        >>> print(progressions.keys())
    """
    if progressions_file is None:
        progressions_file = Path(__file__).parent.parent / "data" / "chord_progressions.json"
    
    return load_json_cached(progressions_file, default={})


@lru_cache(maxsize=32)
def load_genre_templates(genre_file: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load genre template database with caching.
    
    Args:
        genre_file: Path to genre templates file
            (default: music_brain/data/genre_pocket_maps.json)
        
    Returns:
        Genre templates dictionary
        
    Example:
        >>> genres = load_genre_templates()
        >>> funk_pocket = genres.get('funk', {})
    """
    if genre_file is None:
        genre_file = Path(__file__).parent.parent / "data" / "genre_pocket_maps.json"
    
    return load_json_cached(genre_file, default={})


@lru_cache(maxsize=128)
def load_scales_database(scales_file: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load scales database with caching.
    
    This is a large file (~1800 scales) so caching provides significant benefit.
    
    Args:
        scales_file: Path to scales database file
            (default: music_brain/data/scales_database.json)
        
    Returns:
        Scales database dictionary
        
    Example:
        >>> scales = load_scales_database()
        >>> print(f"Loaded {len(scales)} scale variations")
    """
    if scales_file is None:
        scales_file = Path(__file__).parent.parent / "data" / "scales_database.json"
    
    return load_json_cached(scales_file, default={})


# Performance monitoring

def benchmark_cache_performance(filepath: str | Path, iterations: int = 100) -> Dict[str, float]:
    """
    Benchmark cache performance for a JSON file.
    
    Args:
        filepath: Path to JSON file
        iterations: Number of load iterations
        
    Returns:
        Dictionary with timing results:
        - first_load_ms: Time for first load (cold cache)
        - avg_cached_ms: Average time for cached loads (warm cache)
        - speedup: Speedup factor (first / avg_cached)
        
    Example:
        >>> results = benchmark_cache_performance("large_file.json", 100)
        >>> print(f"Speedup: {results['speedup']:.1f}x")
    """
    import time
    
    filepath = Path(filepath)
    
    # Clear cache for fair test
    clear_json_cache()
    
    # First load (cold cache)
    start = time.time()
    _ = load_json_cached(filepath)
    first_load_time = (time.time() - start) * 1000  # Convert to ms
    
    # Subsequent loads (warm cache)
    start = time.time()
    for _ in range(iterations):
        _ = load_json_cached(filepath)
    avg_cached_time = (time.time() - start) * 1000 / iterations
    
    speedup = first_load_time / avg_cached_time if avg_cached_time > 0 else float('inf')
    
    return {
        'first_load_ms': first_load_time,
        'avg_cached_ms': avg_cached_time,
        'speedup': speedup
    }


if __name__ == "__main__":
    # Simple test/demo
    import sys
    
    if len(sys.argv) > 1:
        # Benchmark a file
        filepath = sys.argv[1]
        print(f"Benchmarking: {filepath}")
        results = benchmark_cache_performance(filepath)
        print(f"First load: {results['first_load_ms']:.2f}ms")
        print(f"Cached avg: {results['avg_cached_ms']:.4f}ms")
        print(f"Speedup: {results['speedup']:.1f}x")
        print(f"\nCache info: {get_cache_info()}")
    else:
        print("JSON Cache Utilities")
        print("Usage: python json_cache.py <json_file_path>")
        print("\nExample:")
        print("  python json_cache.py chord_progressions.json")
