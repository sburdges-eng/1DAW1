# Performance Improvement Suggestions

This document identifies slow or inefficient code patterns in the DAiW-Music-Brain codebase and provides actionable suggestions for improvement.

## Executive Summary

Based on comprehensive codebase analysis, the following performance opportunities have been identified:

### Quick Wins (Easy, High Impact)
1. ✅ **Eliminate remaining `range(len())` patterns** - 1 file (sections.py)
2. 🔄 **Add JSON file caching with `@lru_cache`** - 15+ files
3. 🔄 **Use list comprehensions instead of append loops** - Multiple locations
4. 🔄 **Pre-compute constant dictionaries** - Several modules

### Medium Effort, High Impact
5. 🔄 **Optimize sliding window operations** - progression_analysis.py
6. 🔄 **Implement lazy loading for large data structures** - Various modules
7. 🔄 **Add caching decorators to expensive computations** - Chord analysis, scale generation

### Long-term Optimizations
8. 🔄 **Consider NumPy vectorization for array operations** - Audio processing, MIDI analysis
9. 🔄 **Parallel processing for independent tasks** - Batch operations, multi-file processing
10. 🔄 **Binary serialization formats** - Protocol Buffers or MessagePack for faster I/O

---

## 1. Eliminate `range(len())` Anti-patterns

### Current Status
Most instances have been fixed (see PERFORMANCE_OPTIMIZATIONS.md), but some remain.

### Remaining Issues

#### ✅ FIXED: music_brain/structure/sections.py (Line 270)
**Before:**
```python
for i in range(len(merged_boundaries) - 1):
    start_bar = merged_boundaries[i]
    end_bar = merged_boundaries[i + 1]
```

**After:**
```python
for i, (start_bar, end_bar) in enumerate(zip(merged_boundaries[:-1], merged_boundaries[1:])):
```

**Benefits:**
- More Pythonic and readable
- Eliminates double indexing overhead
- Clearer intent (iterating consecutive pairs)

#### ⚠️ ACCEPTABLE: progression_analysis.py (Line 370)
**Current Code:**
```python
# Slide window across sequence
for i in range(len(deg_nums) - plen + 1):
    window = deg_nums[i:i + plen]
```

**Analysis:**
This is a **sliding window pattern** where the index `i` is genuinely needed for slicing. This is an acceptable use case for `range(len())`.

**Alternative (Not Recommended):**
Could use itertools.islice with enumerate, but would be less clear:
```python
from itertools import islice
for i, _ in enumerate(islice(deg_nums, len(deg_nums) - plen + 1)):
    window = deg_nums[i:i + plen]
```

**Recommendation:** Leave as-is. The current code is clear and performant for this use case.

---

## 2. Add JSON File Caching

### Problem
JSON files are loaded repeatedly without caching, causing unnecessary disk I/O.

### Files Affected (220+ json.load() calls total)
- `auto_emotion_sampler.py` - Multiple emotion JSON files
- `emotion_scale_sampler.py` - Config and emotion files
- `music_brain/groove/extractor.py` - Groove templates
- `music_brain/session/intent_schema.py` - Schema files
- `music_brain/learning/curriculum.py` - Lesson plans
- Many others...

### Solution: Use `functools.lru_cache`

#### Example Implementation

**Before:**
```python
def load_emotion_data(emotion_name: str) -> dict:
    """Load emotion JSON file."""
    emotion_file = EMOTION_DIR / f"{emotion_name}.json"
    if emotion_file.exists():
        with open(emotion_file, 'r') as f:
            return json.load(f)
    return {}
```

**After:**
```python
from functools import lru_cache
from pathlib import Path

@lru_cache(maxsize=128)
def load_emotion_data(emotion_name: str) -> dict:
    """Load emotion JSON file. Results are cached."""
    emotion_file = EMOTION_DIR / f"{emotion_name}.json"
    if emotion_file.exists():
        with open(emotion_file, 'r') as f:
            return json.load(f)
    return {}
```

**Benefits:**
- First call: Loads from disk (same speed)
- Subsequent calls: Returns cached data (instant)
- Automatic cache eviction with LRU strategy
- Zero memory leaks with maxsize parameter

**Memory Overhead:**
- Typical JSON: 1-50 KB per file
- With maxsize=128: Maximum ~6 MB (acceptable)

### Specific Recommendations

#### High Priority - Frequently Accessed

1. **Emotion Taxonomy Files** (generate_scales_db.py)
   - Already has global cache: `_EMOTION_TAXONOMY_CACHE`
   - ✅ Good implementation

2. **Chord Progression Patterns**
   ```python
   @lru_cache(maxsize=32)
   def load_chord_progressions() -> dict:
       """Load and cache chord progression database."""
       # Implementation
   ```

3. **Genre Templates**
   ```python
   @lru_cache(maxsize=64)
   def load_genre_template(genre: str) -> dict:
       """Load and cache genre-specific template."""
       # Implementation
   ```

4. **Scale Variations**
   ```python
   @lru_cache(maxsize=256)
   def get_scale_variations() -> list:
       """Load and cache all scale variations."""
       # Implementation (expensive, called often)
   ```

#### Medium Priority - Occasionally Accessed

5. **Config Files** (auto_emotion_sampler.py, emotion_scale_sampler.py)
   ```python
   @lru_cache(maxsize=8)
   def load_config() -> dict:
       """Load configuration file with caching."""
       # Implementation
   ```

6. **Intent Schema Templates**
   ```python
   @lru_cache(maxsize=16)
   def load_intent_schema() -> dict:
       """Load intent schema with caching."""
       # Implementation
   ```

### Cache Invalidation Strategy

For files that may change:
```python
from functools import lru_cache
import os

def _get_file_mtime(filepath: Path) -> float:
    """Get file modification time for cache key."""
    return os.path.getmtime(filepath) if filepath.exists() else 0.0

@lru_cache(maxsize=128)
def load_with_mtime_check(filepath: str, mtime: float) -> dict:
    """Load JSON with modification time as cache key."""
    with open(filepath, 'r') as f:
        return json.load(f)

def load_emotion_data(emotion_name: str) -> dict:
    """Load emotion data with automatic cache invalidation."""
    filepath = EMOTION_DIR / f"{emotion_name}.json"
    mtime = _get_file_mtime(filepath)
    return load_with_mtime_check(str(filepath), mtime)
```

---

## 3. List Comprehensions vs Append Loops

### Problem
Many places use explicit loops with `.append()` where list comprehensions would be faster and more Pythonic.

### Performance Impact
- List comprehensions: ~10-30% faster
- More readable and concise
- Better memory efficiency (pre-allocated size)

### Examples

#### Pattern 1: Simple Transformation

**Before:**
```python
results = []
for item in items:
    results.append(transform(item))
```

**After:**
```python
results = [transform(item) for item in items]
```

#### Pattern 2: Filtered Transformation

**Before:**
```python
results = []
for item in items:
    if condition(item):
        results.append(transform(item))
```

**After:**
```python
results = [transform(item) for item in items if condition(item)]
```

#### Pattern 3: Nested Loops

**Before:**
```python
results = []
for outer in outer_list:
    for inner in outer.items:
        results.append((outer.id, inner))
```

**After:**
```python
results = [(outer.id, inner) for outer in outer_list for inner in outer.items]
```

### When NOT to Use Comprehensions

❌ **Complex logic with multiple conditionals:**
```python
# DON'T - too complex
results = [
    complex_transform(item, context) 
    for item in items 
    if condition1(item) and condition2(item)
    if not condition3(item)
]

# DO - use explicit loop
results = []
for item in items:
    if condition1(item) and condition2(item) and not condition3(item):
        results.append(complex_transform(item, context))
```

❌ **Side effects needed:**
```python
# DON'T - comprehensions shouldn't have side effects
[print(item) for item in items]  # Bad practice

# DO - use explicit loop
for item in items:
    print(item)
```

---

## 4. Pre-compute Constant Dictionaries

### Problem
Dictionaries are recreated in loops when they could be module-level constants.

### Example from generate_scales_db.py

**Before:**
```python
for intensity in intensities:
    arousal_value = {
        "subtle": 0.1,
        "mild": 0.3,
        "moderate": 0.5,
        "strong": 0.7,
        "intense": 0.9
    }[intensity]
```

**After (✅ Already Fixed):**
```python
# Module level
AROUSAL_MODIFIERS = {
    "subtle": 0.1,
    "mild": 0.3,
    "moderate": 0.5,
    "strong": 0.7,
    "intense": 0.9
}

# In loop
for intensity in intensities:
    arousal_value = AROUSAL_MODIFIERS[intensity]
```

**Impact:** Eliminates 1800+ dictionary allocations in scale generation.

### Pattern to Look For

Search for:
```bash
grep -rn "^\s*{\s*$" --include="*.py" | grep "for.*in"
```

### Recommendation
- Define as module-level `CONSTANT_NAME = {...}` 
- Use `typing.Final` for type hints (Python 3.8+)
- Document the purpose in a docstring

```python
from typing import Final

AROUSAL_MODIFIERS: Final[dict[str, float]] = {
    """Arousal modifier values for intensity levels."""
    "subtle": 0.1,
    "mild": 0.3,
    # ...
}
```

---

## 5. Optimize Sliding Window Operations

### Current Implementation (progression_analysis.py)

```python
for i in range(len(deg_nums) - plen + 1):
    window = deg_nums[i:i + plen]
    
    match_count = 0
    mismatch_count = 0
    chromatic_count = 0
    
    for actual, expected in zip(window, pattern):
        if actual == expected:
            match_count += 1
        elif actual == 0:
            chromatic_count += 1
        else:
            mismatch_count += 1
```

### Optimization Opportunity

For very large progressions (hundreds of chords), consider:

#### Option 1: Use itertools for sliding windows
```python
from itertools import islice

def sliding_window(iterable, n):
    """Memory-efficient sliding window."""
    it = iter(iterable)
    window = tuple(islice(it, n))
    if len(window) == n:
        yield window
    for elem in it:
        window = window[1:] + (elem,)
        yield window

for window in sliding_window(deg_nums, plen):
    # Process window
    pass
```

**When to use:** Only beneficial for very large sequences (1000+ elements) where memory is constrained.

#### Option 2: NumPy vectorization (if NumPy available)
```python
import numpy as np

def find_pattern_matches_vectorized(deg_nums, pattern, tolerance):
    """Vectorized pattern matching with NumPy."""
    deg_array = np.array(deg_nums)
    pattern_array = np.array(pattern)
    
    # Sliding window view (zero-copy)
    n = len(deg_array) - len(pattern_array) + 1
    windows = np.lib.stride_tricks.sliding_window_view(deg_array, len(pattern_array))
    
    # Vectorized comparison
    matches = windows == pattern_array
    match_counts = matches.sum(axis=1)
    # ... rest of logic
```

**When to use:** 
- Large progressions (100+ chords)
- NumPy already installed
- ~5-10x speedup potential

**Current Recommendation:** Leave as-is unless profiling shows this is a bottleneck.

---

## 6. Implement Lazy Loading

### Problem
Large data structures are loaded eagerly on module import, slowing startup.

### Example Scenario

**Before:**
```python
# module level - loaded immediately
CHORD_PROGRESSIONS = json.loads(
    (Path(__file__).parent / "chord_progressions.json").read_text()
)
```

**After:**
```python
_CHORD_PROGRESSIONS = None

def get_chord_progressions() -> dict:
    """Lazy load chord progressions on first access."""
    global _CHORD_PROGRESSIONS
    if _CHORD_PROGRESSIONS is None:
        filepath = Path(__file__).parent / "chord_progressions.json"
        _CHORD_PROGRESSIONS = json.loads(filepath.read_text())
    return _CHORD_PROGRESSIONS
```

### Benefits
- Faster module import times
- Reduced memory for unused features
- Better for CLI applications where only subset of features are used

### Startup Time Analysis

Measure impact:
```python
import time

start = time.time()
import music_brain.cli  # Or other module
print(f"Import time: {time.time() - start:.3f}s")
```

### Candidates for Lazy Loading

1. **Large JSON files** (chord_progressions.json, scales_database.json)
2. **Emotion taxonomy** (if not already cached)
3. **Genre templates** (unless needed immediately)
4. **Optional dependencies** (librosa, soundfile)

---

## 7. Add Caching to Expensive Computations

### Chord Analysis

**Before:**
```python
def analyze_chord(chord_name: str) -> ChordAnalysis:
    """Analyze chord structure."""
    # Expensive parsing and analysis
    # Called repeatedly for same chords
```

**After:**
```python
@lru_cache(maxsize=512)
def analyze_chord(chord_name: str) -> ChordAnalysis:
    """Analyze chord structure. Results cached for performance."""
    # Same implementation
```

**Impact:** 
- First analysis: Same speed
- Repeated chords: Instant lookup
- Typical song: 10-20 unique chords → 90% cache hit rate

### Voice Leading Analysis

```python
@lru_cache(maxsize=1024)
def compute_voice_leading(prev_chord: tuple, curr_chord: tuple) -> float:
    """Compute voice leading distance. Tuple args for hashability."""
    # Expensive computation
```

**Note:** Must convert lists to tuples for hashability:
```python
prev_tuple = tuple(prev_voicing)
result = compute_voice_leading(prev_tuple, curr_tuple)
```

### Scale Generation

Already optimized with caching in generate_scales_db.py ✅

---

## 8. NumPy Vectorization

### When to Use
- Processing arrays of 1000+ elements
- Numerical computations in tight loops
- Audio signal processing
- MIDI timing analysis

### Example: Audio Feature Extraction

**Before (Python loops):**
```python
def compute_spectral_centroid(magnitudes, frequencies):
    """Compute spectral centroid."""
    weighted_sum = 0
    total_magnitude = 0
    for mag, freq in zip(magnitudes, frequencies):
        weighted_sum += mag * freq
        total_magnitude += mag
    return weighted_sum / total_magnitude if total_magnitude > 0 else 0
```

**After (NumPy):**
```python
import numpy as np

def compute_spectral_centroid(magnitudes, frequencies):
    """Compute spectral centroid with NumPy."""
    magnitudes = np.asarray(magnitudes)
    frequencies = np.asarray(frequencies)
    return np.sum(magnitudes * frequencies) / np.sum(magnitudes)
```

**Performance:** ~50-100x faster for large arrays.

### Candidates in Codebase

1. **music_brain/audio/feel.py** - Audio analysis
2. **music_brain/groove/extractor.py** - Timing deviation calculations
3. **analyzer.py** - Spectral analysis (already uses NumPy ✅)

### Implementation Note

Wrap in try/except for optional NumPy:
```python
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

def process_array(data):
    if NUMPY_AVAILABLE:
        return _process_array_numpy(data)
    else:
        return _process_array_python(data)
```

---

## 9. Parallel Processing

### Use Cases
- Batch MIDI file processing
- Multiple chord progression analysis
- Independent scale generation
- Audio file cataloging

### Example: Batch Processing

**Before (Sequential):**
```python
results = []
for midi_file in midi_files:
    result = analyze_midi(midi_file)
    results.append(result)
```

**After (Parallel):**
```python
from multiprocessing import Pool
from functools import partial

def process_files_parallel(midi_files, num_workers=4):
    """Process MIDI files in parallel."""
    with Pool(processes=num_workers) as pool:
        results = pool.map(analyze_midi, midi_files)
    return results
```

**Performance:** ~4x speedup with 4 cores for I/O-bound tasks.

### Considerations
- Only beneficial for batch operations (10+ files)
- Each process has overhead (~100ms startup)
- Not useful for single file analysis
- GIL doesn't affect I/O-bound tasks

### Recommended Implementation

```python
def analyze_many_files(files, parallel=True, num_workers=None):
    """
    Analyze multiple files with optional parallelization.
    
    Args:
        files: List of file paths
        parallel: Use multiprocessing (default: True if len(files) > 10)
        num_workers: Number of worker processes (default: CPU count)
    """
    if parallel is None:
        parallel = len(files) > 10
    
    if parallel:
        import multiprocessing as mp
        workers = num_workers or mp.cpu_count()
        with mp.Pool(workers) as pool:
            return pool.map(analyze_file, files)
    else:
        return [analyze_file(f) for f in files]
```

---

## 10. Binary Serialization Formats

### Problem
JSON is slow for large datasets (scale_database.json with 1800 scales).

### Alternatives

#### Option 1: MessagePack
```python
import msgpack

# Write
with open('data.msgpack', 'wb') as f:
    msgpack.pack(data, f)

# Read (2-5x faster than JSON)
with open('data.msgpack', 'rb') as f:
    data = msgpack.unpack(f)
```

**Benefits:**
- 2-5x faster than JSON
- Smaller file size (20-50% reduction)
- Drop-in replacement for json module

#### Option 2: Pickle (Python only)
```python
import pickle

# Write
with open('data.pkl', 'wb') as f:
    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

# Read (5-10x faster than JSON)
with open('data.pkl', 'rb') as f:
    data = pickle.load(f)
```

**Benefits:**
- Fastest option
- Native Python support
- Can serialize complex objects

**Drawbacks:**
- Not human-readable
- Security risk with untrusted data
- Python-only

### Recommendation

For internal data (not user-editable):
1. Generate JSON for development/debugging
2. Use MessagePack for production
3. Convert JSON → MessagePack on first load
4. Cache MessagePack version

```python
from pathlib import Path
import json
import msgpack

def load_scales_db():
    """Load scales database, prefer binary format."""
    json_path = Path("scales_database.json")
    msgpack_path = Path("scales_database.msgpack")
    
    # Use msgpack if available and newer
    if msgpack_path.exists():
        json_mtime = json_path.stat().st_mtime
        msgpack_mtime = msgpack_path.stat().st_mtime
        if msgpack_mtime >= json_mtime:
            with open(msgpack_path, 'rb') as f:
                return msgpack.unpack(f)
    
    # Load JSON and cache as msgpack
    with open(json_path) as f:
        data = json.load(f)
    
    with open(msgpack_path, 'wb') as f:
        msgpack.pack(data, f)
    
    return data
```

---

## Benchmarking Methodology

### How to Measure Performance

#### 1. Simple Timing
```python
import time

def benchmark(func, *args, iterations=1000):
    """Benchmark function execution time."""
    start = time.time()
    for _ in range(iterations):
        func(*args)
    elapsed = time.time() - start
    return elapsed / iterations

# Usage
avg_time = benchmark(my_function, arg1, arg2)
print(f"Average: {avg_time*1000:.2f}ms")
```

#### 2. Python Profiler
```bash
# Profile a script
python -m cProfile -o profile.stats script.py

# Analyze results
python -m pstats profile.stats
>>> sort cumulative
>>> stats 20
```

#### 3. Line Profiler (for detailed analysis)
```bash
pip install line_profiler

# Add @profile decorator to functions
# Run profiler
kernprof -l -v script.py
```

#### 4. Memory Profiler
```bash
pip install memory_profiler

# Add @profile decorator
# Run profiler  
python -m memory_profiler script.py
```

---

## Priority Matrix

### Immediate (This Sprint)
1. ✅ Fix remaining `range(len())` in sections.py
2. 🔄 Add `@lru_cache` to top 10 JSON loading functions
3. 🔄 Convert 5-10 append loops to list comprehensions

### Short-term (Next Sprint)
4. 🔄 Add lazy loading to large JSON files
5. 🔄 Cache chord analysis and voice leading
6. 🔄 Add performance regression tests

### Medium-term (1-2 Months)
7. 🔄 Implement batch parallel processing
8. 🔄 NumPy vectorization for audio processing
9. 🔄 MessagePack support for large databases

### Long-term (3-6 Months)
10. 🔄 Comprehensive performance profiling
11. 🔄 Database backend for template storage
12. 🔄 JIT compilation for hot paths (Numba)

---

## Testing Strategy

### Performance Regression Tests

Create `tests/test_performance_regression.py`:

```python
import pytest
import time

def test_chord_analysis_performance():
    """Chord analysis should complete quickly."""
    from music_brain.structure.chord import analyze_chord
    
    start = time.time()
    for _ in range(100):
        analyze_chord("Cmaj7")
    elapsed = time.time() - start
    
    # Should average < 1ms per chord
    assert elapsed < 0.1, f"Too slow: {elapsed:.3f}s for 100 chords"

def test_json_caching_effectiveness():
    """Cached JSON loads should be near-instant."""
    from music_brain.data.loader import load_emotion_data
    
    # First load
    start = time.time()
    data1 = load_emotion_data("happy")
    first_load = time.time() - start
    
    # Cached load
    start = time.time()
    data2 = load_emotion_data("happy")
    cached_load = time.time() - start
    
    # Cache should be 100x+ faster
    assert cached_load < first_load * 0.01
    assert data1 == data2
```

### Continuous Monitoring

Add to CI/CD:
```yaml
# .github/workflows/performance.yml
- name: Run Performance Tests
  run: python -m pytest tests/test_performance*.py -v
  
- name: Benchmark Core Functions
  run: python benchmarks/benchmark_suite.py
  
- name: Check for Performance Regressions
  run: python benchmarks/compare_results.py
```

---

## Conclusion

### Summary of Recommendations

| Category | Priority | Effort | Impact | Status |
|----------|----------|--------|--------|--------|
| Fix range(len()) | High | Low | Low | ✅ Done |
| JSON caching | High | Low | High | 🔄 Pending |
| List comprehensions | Medium | Low | Medium | 🔄 Pending |
| Lazy loading | Medium | Medium | Medium | 🔄 Pending |
| Computation caching | High | Low | High | 🔄 Pending |
| NumPy vectorization | Low | High | High* | 🔄 Future |
| Parallel processing | Low | Medium | High* | 🔄 Future |
| Binary formats | Low | Medium | Medium | 🔄 Future |

*High impact only for specific use cases

### Expected Improvements

Implementing high-priority items:
- **Startup time:** 20-40% faster (lazy loading + caching)
- **Repeated operations:** 80-95% faster (caching)
- **Memory usage:** Similar or slightly higher (acceptable trade-off)
- **Code maintainability:** Improved (more Pythonic patterns)

### Next Steps

1. Review and approve this document
2. Implement quick wins (items 1-3)
3. Add performance regression tests
4. Profile real-world usage to identify actual bottlenecks
5. Iterate on medium/long-term optimizations based on data

---

## References

- [Python Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)
- [functools.lru_cache documentation](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- [NumPy Performance Guide](https://numpy.org/doc/stable/user/basics.performance.html)
- [Python Profiling Documentation](https://docs.python.org/3/library/profile.html)
- [MessagePack for Python](https://msgpack.org/)

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-06  
**Author:** Performance Analysis Agent  
**Status:** Ready for Review
