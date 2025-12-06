"""
Tests for JSON caching utilities.

Tests caching behavior, cache invalidation, and performance.
"""

import json
import tempfile
import time
from pathlib import Path


def test_load_json_cached_basic():
    """Test basic JSON caching functionality."""
    from music_brain.utils.json_cache import load_json_cached, clear_json_cache
    
    # Create a temporary JSON file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_data = {"name": "test", "value": 123}
        json.dump(test_data, f)
        temp_path = f.name
    
    try:
        # Clear cache
        clear_json_cache()
        
        # First load
        data1 = load_json_cached(temp_path)
        assert data1 == test_data
        
        # Second load (should be cached)
        data2 = load_json_cached(temp_path)
        assert data2 == test_data
        
        # Should be same object due to caching
        assert data1 is data2
        
    finally:
        # Cleanup
        Path(temp_path).unlink()


def test_cache_invalidation_on_file_change():
    """Test that cache is invalidated when file is modified."""
    from music_brain.utils.json_cache import load_json_cached, clear_json_cache
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        initial_data = {"version": 1}
        json.dump(initial_data, f)
        temp_path = f.name
    
    try:
        clear_json_cache()
        
        # First load
        data1 = load_json_cached(temp_path)
        assert data1["version"] == 1
        
        # Modify file
        time.sleep(0.01)  # Ensure different mtime
        with open(temp_path, 'w') as f:
            updated_data = {"version": 2}
            json.dump(updated_data, f)
        
        # Load again - should see updated data
        data2 = load_json_cached(temp_path)
        assert data2["version"] == 2
        
        # Should be different objects (cache was invalidated)
        assert data1 is not data2
        
    finally:
        Path(temp_path).unlink()


def test_cache_performance():
    """Test that caching provides performance benefit."""
    from music_brain.utils.json_cache import load_json_cached, clear_json_cache
    
    # Create a moderately sized JSON file
    test_data = {
        "items": [{"id": i, "name": f"item_{i}", "values": list(range(10))} 
                  for i in range(100)]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_path = f.name
    
    try:
        clear_json_cache()
        
        # First load (cold cache)
        start = time.time()
        _ = load_json_cached(temp_path)
        first_load = time.time() - start
        
        # Second load (warm cache)
        start = time.time()
        _ = load_json_cached(temp_path)
        cached_load = time.time() - start
        
        # Cached load should be much faster (at least 5x)
        speedup = first_load / cached_load if cached_load > 0 else float('inf')
        print(f"\n  First load: {first_load*1000:.2f}ms")
        print(f"  Cached load: {cached_load*1000:.4f}ms")
        print(f"  Speedup: {speedup:.1f}x")
        
        assert cached_load < first_load * 0.2, \
            f"Cache not effective: speedup only {speedup:.1f}x"
        
    finally:
        Path(temp_path).unlink()


def test_default_value():
    """Test that default value is returned for missing files."""
    from music_brain.utils.json_cache import load_json_cached
    import tempfile
    
    # Create a path that doesn't exist (cross-platform)
    nonexistent_path = Path(tempfile.gettempdir()) / "nonexistent_file_12345.json"
    
    result = load_json_cached(nonexistent_path, default={})
    assert result == {}
    
    result = load_json_cached(nonexistent_path, default={"fallback": True})
    assert result == {"fallback": True}


def test_cache_info():
    """Test cache statistics."""
    from music_brain.utils.json_cache import (
        load_json_cached, 
        clear_json_cache, 
        get_cache_info
    )
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"test": "data"}, f)
        temp_path = f.name
    
    try:
        clear_json_cache()
        
        # Initial stats
        info = get_cache_info()
        initial_misses = info['misses']
        initial_hits = info['hits']
        
        # First load (miss)
        _ = load_json_cached(temp_path)
        info = get_cache_info()
        assert info['misses'] == initial_misses + 1
        
        # Second load (hit)
        _ = load_json_cached(temp_path)
        info = get_cache_info()
        assert info['hits'] == initial_hits + 1
        
    finally:
        Path(temp_path).unlink()


def test_emotion_file_loader():
    """Test emotion file loader (if emotion files exist)."""
    try:
        from music_brain.utils.json_cache import load_emotion_file
        
        # Try to load a known emotion file
        # This will only work if emotion_thesaurus directory exists
        try:
            happy_data = load_emotion_file("happy")
            assert isinstance(happy_data, dict)
            
            # Second load should be instant
            happy_data2 = load_emotion_file("happy")
            assert happy_data is happy_data2  # Same object (cached)
            
        except FileNotFoundError:
            # Emotion files don't exist in test environment
            pass
            
    except ImportError:
        # Module not available
        pass


def test_chord_progressions_loader():
    """Test chord progressions loader (if file exists)."""
    try:
        from music_brain.utils.json_cache import load_chord_progressions
        
        try:
            progressions = load_chord_progressions()
            assert isinstance(progressions, dict)
            
            # Second load should be cached
            progressions2 = load_chord_progressions()
            assert progressions is progressions2
            
        except FileNotFoundError:
            # File doesn't exist in test environment
            pass
            
    except ImportError:
        pass


if __name__ == "__main__":
    print("Running JSON cache tests...\n")
    
    tests = [
        ("Basic caching", test_load_json_cached_basic),
        ("Cache invalidation", test_cache_invalidation_on_file_change),
        ("Cache performance", test_cache_performance),
        ("Default value", test_default_value),
        ("Cache info", test_cache_info),
        ("Emotion file loader", test_emotion_file_loader),
        ("Chord progressions loader", test_chord_progressions_loader),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            print(f"{name}...", end=" ")
            test_func()
            print("✓ PASSED")
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            failed += 1
        except (ImportError, FileNotFoundError) as e:
            print(f"⊘ SKIPPED: {type(e).__name__}: {e}")
        except Exception as e:
            print(f"⊘ ERROR ({type(e).__name__}): {e}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*60}")
