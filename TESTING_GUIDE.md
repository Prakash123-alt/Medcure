# Testing Guide for Medical AI Agent

## 📋 Overview

This guide covers how to test all components of the Medical AI Agent system, including the newly implemented enhancements.

---

## 🛠️ Setup

### 1. Install Dependencies:
```bash
# Core dependencies
pip install -r requirements_rag.txt
pip install -r requirements_notifications.txt

# Enhancement dependencies
pip install -r requirements_enhancements.txt

# Testing dependencies
pip install -r requirements_testing.txt
```

### 2. Setup Redis (for caching tests):
```bash
# Windows - using Chocolatey
choco install redis-64

# Or Docker
docker run -d --name redis-test -p 6379:6379 redis:latest

# Verify
redis-cli ping  # Should return: PONG
```

### 3. Configure Environment:
```bash
# Optional: Set test environment variables
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
export REDIS_CACHE_ENABLED="true"
```

---

## 🧪 Running Tests

### Run All Tests:
```bash
pytest
```

### Run Specific Test Files:
```bash
# Drug interaction tests
pytest tests/test_drug_interactions.py -v

# Medication scheduler tests
pytest tests/test_medication_scheduler.py -v

# RAG caching tests
pytest tests/test_rag_cache.py -v

# Integration tests
pytest tests/test_integration.py -v
```

### Run Tests by Marker:
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Tests requiring Redis
pytest -m requires_redis

# Tests requiring database
pytest -m requires_db

# Slow tests
pytest -m slow
```

### Run with Coverage:
```bash
# Generate HTML coverage report
pytest --cov=medical_ai_agent --cov-report=html

# Generate terminal report
pytest --cov=medical_ai_agent --cov-report=term-missing

# View HTML report
# Windows
start htmlcov/index.html

# Linux/Mac
open htmlcov/index.html
```

### Run Tests in Parallel:
```bash
# Install pytest-xdist
pip install pytest-xdist

# Run with 4 workers
pytest -n 4
```

---

## 📊 Test Structure

### 1. Drug Interaction Tests (`test_drug_interactions.py`)

**Total Tests:** 12

#### Test Cases:
- ✅ `test_drug_drug_interaction_detected` - Detects known drug-drug interactions
- ✅ `test_drug_disease_contraindication` - Identifies contraindications for chronic conditions
- ✅ `test_allergy_checking` - Cross-references allergies with drug classes
- ✅ `test_renal_dosage_adjustment` - Recommends dosage adjustments for impaired renal function
- ✅ `test_elderly_patient_dosage` - Flags dosage concerns for elderly patients
- ✅ `test_no_interactions_clean_case` - Validates clean prescriptions return no interactions
- ✅ `test_severity_ordering` - Verifies interactions are severity-ordered
- ✅ `test_multiple_interactions_same_drug` - Detects multiple interaction types

#### Sample Output:
```bash
$ pytest tests/test_drug_interactions.py -v

tests/test_drug_interactions.py::test_drug_drug_interaction_detected PASSED  [ 8%]
tests/test_drug_interactions.py::test_drug_disease_contraindication PASSED  [16%]
tests/test_drug_interactions.py::test_allergy_checking PASSED               [25%]
tests/test_drug_interactions.py::test_renal_dosage_adjustment PASSED        [33%]
...

======================== 12 passed in 1.23s ========================
```

---

### 2. Medication Scheduler Tests (`test_medication_scheduler.py`)

**Total Tests:** 11

#### Test Cases:
- ✅ `test_parse_frequency_numeric_notation` - Parses 1-0-1 format
- ✅ `test_parse_frequency_text_notation` - Parses "twice daily", etc.
- ✅ `test_meal_timing_extraction` - Extracts before/after/with meals
- ✅ `test_calculate_optimal_times` - Calculates medication times
- ✅ `test_adjust_for_meal_timing` - Adjusts times for meal requirements
- ✅ `test_generate_medicine_schedule` - Creates complete schedule for medicine
- ✅ `test_generate_full_schedule` - Generates schedule for multiple medicines
- ✅ `test_estimate_duration` - Estimates treatment duration
- ✅ `test_daily_summary_generation` - Creates daily medication summary
- ✅ `test_custom_meal_times` - Uses custom meal timing
- ✅ `test_prn_medication_handling` - Handles "as needed" medications

#### Sample Output:
```bash
$ pytest tests/test_medication_scheduler.py -v

tests/test_medication_scheduler.py::test_parse_frequency_numeric_notation PASSED  [ 9%]
tests/test_medication_scheduler.py::test_parse_frequency_text_notation PASSED    [18%]
...

======================== 11 passed in 0.95s ========================
```

---

### 3. RAG Cache Tests (`test_rag_cache.py`)

**Total Tests:** 14

#### Test Cases:
- ✅ `test_cache_initialization_success` - Successful Redis connection
- ✅ `test_cache_initialization_failure` - Handles connection failure
- ✅ `test_cache_disabled` - Behavior when caching disabled
- ✅ `test_generate_cache_key` - Generates deterministic keys
- ✅ `test_cache_miss` - Handles cache miss
- ✅ `test_cache_hit` - Retrieves cached data
- ✅ `test_cache_set` - Stores data with TTL
- ✅ `test_cache_invalidate_specific_query` - Invalidates specific query
- ✅ `test_cache_invalidate_pattern` - Invalidates by pattern
- ✅ `test_cache_clear_all` - Clears all cache entries
- ✅ `test_cache_stats` - Retrieves cache statistics
- ✅ `test_cache_health_check` - Health check
- ✅ `test_singleton_pattern` - Singleton implementation
- ✅ `test_cache_key_deterministic` - Key consistency
- ✅ `test_cache_with_filters` - Keys with metadata filters
- ✅ `test_cache_ttl_default` - Default TTL
- ✅ `test_cache_ttl_custom` - Custom TTL

#### Sample Output:
```bash
$ pytest tests/test_rag_cache.py -v

tests/test_rag_cache.py::test_cache_initialization_success PASSED  [ 7%]
tests/test_rag_cache.py::test_cache_miss PASSED                    [14%]
tests/test_rag_cache.py::test_cache_hit PASSED                     [21%]
...

======================== 14 passed in 1.45s ========================
```

---

### 4. Integration Tests (`test_integration.py`)

**Total Tests:** 7

#### Test Cases:
- ✅ `test_complete_workflow_with_enhancements` - Full system workflow
- ✅ `test_critical_interaction_flags_human_review` - Human review triggers
- ✅ `test_medication_schedule_with_meal_timing` - Meal timing integration
- ✅ `test_rag_with_caching` - RAG cache integration
- ✅ `test_patient_bmi_and_renal_calculations` - Patient calculations
- ✅ `test_notification_with_scheduler_integration` - Notification + scheduler

#### Sample Output:
```bash
$ pytest tests/test_integration.py -v

tests/test_integration.py::test_complete_workflow_with_enhancements PASSED  [14%]
tests/test_integration.py::test_critical_interaction_flags_human_review PASSED [28%]
...

======================== 7 passed in 2.31s ========================
```

---

## 🎯 Manual Testing

### 1. Test Drug Interaction Checker:
```python
from medical_ai_agent.drug_interaction_checker import DrugInteractionChecker
from medical_ai_agent.models import Medicine, PatientContext

# Create checker
checker = DrugInteractionChecker()

# Define medicines
medicines = [
    Medicine(name="Aspirin", strength="100mg", frequency="1-0-1"),
    Medicine(name="Warfarin", strength="5mg", frequency="1-0-0")
]

# Define patient
patient = PatientContext(
    patient_id="TEST_001",
    age=65,
    gender="Male",
    weight_kg=70.0,
    height_cm=170.0,
    chronic_conditions=["Atrial Fibrillation"],
    allergies=[]
)

# Check interactions
interactions = checker.check_all_interactions(medicines, patient)

# Display results
for interaction in interactions:
    print(f"{interaction.severity.upper()}: {interaction.drug1} + {interaction.drug2}")
    print(f"  {interaction.description}")
    print(f"  Recommendation: {interaction.recommendation}\n")
```

**Expected Output:**
```
SEVERE: Aspirin + Warfarin
  Increased bleeding risk. Both drugs affect clotting.
  Recommendation: Monitor INR closely. Consider alternative pain relief.
```

---

### 2. Test Medication Scheduler:
```python
from medical_ai_agent.medication_scheduler import get_schedule_generator
from medical_ai_agent.models import Medicine, PatientContext

# Create scheduler
scheduler = get_schedule_generator()

# Define medicines
medicines = [
    Medicine(
        name="Metformin",
        strength="500mg",
        frequency="1-0-1",
        instructions="Take with meals",
        duration_days=30
    ),
    Medicine(
        name="Atorvastatin",
        strength="10mg",
        frequency="0-0-1",
        instructions="Take at bedtime",
        duration_days=30
    )
]

# Define patient
patient = PatientContext(
    patient_id="TEST_001",
    age=55,
    gender="Male",
    weight_kg=75.0,
    height_cm=170.0,
    phone_number="+919876543210",
    preferred_language="en"
)

# Generate schedule
schedules = scheduler.generate_schedule(
    medicines=medicines,
    patient_context=patient,
    start_date="2024-02-01"
)

# Daily summary
summary = scheduler.generate_daily_summary(schedules, date="2024-02-01")
print(summary)
```

**Expected Output:**
```
Medications for 2024-02-01:

08:00:
  • Metformin (500mg) - Take with meals

20:00:
  • Metformin (500mg) - Take with meals
  • Atorvastatin (10mg) - Take at bedtime
```

---

### 3. Test RAG Cache:
```python
from medical_ai_agent.rag_cache import get_rag_cache

# Get cache instance
cache = get_rag_cache(enabled=True)

# Check health
if cache.health_check():
    print("✓ Cache is healthy")
else:
    print("✗ Cache is unavailable")

# Set data
results = [
    {"content": "AIIMS guideline for diabetes", "metadata": {"source": "AIIMS"}}
]
cache.set("diabetes treatment", results, k=3, ttl=3600)

# Get data
cached = cache.get("diabetes treatment", k=3)
if cached:
    print(f"✓ Cache HIT: {len(cached)} results")
else:
    print("✗ Cache MISS")

# Get stats
stats = cache.get_stats()
print(f"\nCache Statistics:")
print(f"  Total Keys: {stats['total_keys']}")
print(f"  Hit Rate: {stats['hit_rate']:.1f}%")
```

**Expected Output:**
```
✓ Cache is healthy
✓ Cache HIT: 1 results

Cache Statistics:
  Total Keys: 1
  Hit Rate: 100.0%
```

---

## 🔍 Debugging Tests

### Run Single Test:
```bash
pytest tests/test_drug_interactions.py::test_drug_drug_interaction_detected -v
```

### Run with Debug Output:
```bash
pytest tests/test_drug_interactions.py -v -s
```

### Run with PDB on Failure:
```bash
pytest tests/test_drug_interactions.py --pdb
```

### Run Failed Tests Only:
```bash
pytest --lf
```

---

## 📈 Coverage Goals

### Target Coverage:
- **Overall:** ≥80%
- **Drug Interaction Checker:** ≥90%
- **Medication Scheduler:** ≥85%
- **RAG Cache:** ≥85%
- **Integration:** ≥70%

### Check Coverage:
```bash
pytest --cov=medical_ai_agent --cov-report=term-missing

# View detailed report
pytest --cov=medical_ai_agent --cov-report=html
start htmlcov/index.html
```

---

## 🐛 Common Issues

### Issue 1: Redis Connection Failed
**Error:** `ConnectionRefusedError: [Errno 111] Connection refused`

**Solution:**
```bash
# Check if Redis is running
redis-cli ping

# If not, start Redis
# Windows:
redis-server

# Docker:
docker start redis-test
```

### Issue 2: Import Errors
**Error:** `ModuleNotFoundError: No module named 'medical_ai_agent'`

**Solution:**
```bash
# Install in development mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/medcure_GDGE"
```

### Issue 3: Async Tests Failing
**Error:** `RuntimeError: no running event loop`

**Solution:**
- Ensure `pytest-asyncio` is installed
- Check `pytest.ini` has `asyncio_mode = auto`
- Use `@pytest.mark.asyncio` decorator

---

## ✅ Test Checklist

Before committing changes:

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Coverage ≥80%
- [ ] No failing tests
- [ ] New features have corresponding tests
- [ ] Documentation updated
- [ ] No debug print statements left

---

## 📝 Writing New Tests

### Test Template:
```python
import pytest
from medical_ai_agent.your_module import YourClass

@pytest.fixture
def sample_data():
    """Create sample test data."""
    return YourClass(param="value")

def test_your_feature(sample_data):
    """Test your feature."""
    result = sample_data.method()
    
    assert result is not None
    assert result.property == "expected"

@pytest.mark.asyncio
async def test_async_feature():
    """Test async feature."""
    result = await async_function()
    assert result == "expected"
```

### Best Practices:
1. **One assertion per test** (when possible)
2. **Use descriptive test names**
3. **Setup with fixtures**
4. **Clean up after tests**
5. **Mock external dependencies**
6. **Test edge cases**
7. **Test error handling**

---

## 🚀 Continuous Integration

### GitHub Actions Example:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements_testing.txt
        pip install -e .
    
    - name: Run tests
      run: pytest --cov=medical_ai_agent --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## 📞 Support

For testing issues:
- Check `IMPLEMENTATION_COMPLETE.md` for system overview
- Review individual test files for examples
- Ensure all dependencies are installed

---

**Happy Testing!** 🧪✅
