# Data Integrity Checker

## Status: ✅ WORKING!

The integrity checker now uses **Archives of Nethys' official Elasticsearch API** to validate and fix data. This is fast, reliable, and doesn't require any web scraping!

## Features

- ✅ Check random sample or ALL items
- ✅ Compare with AoN's official database
- ✅ Automatically fix mismatched data with `--replace` flag
- ✅ Fast and reliable (no rate limiting or CAPTCHAs)

## Usage

```bash
python bin/check_data_integrity.py [num_checks|all] [data_type] [--replace]
```

### Parameters
- `num_checks`: Number of random items to check, or `all` to check everything (default: 10)
- `data_type`: Type of data - 'equipment' or 'creatures' (default: equipment)
- `--replace`: Update mismatched items with correct AoN data

### Examples

**Check random samples:**
```bash
# Check 10 random equipment items
python bin/check_data_integrity.py 10 equipment

# Check 5 random creatures
python bin/check_data_integrity.py 5 creatures
```

**Check everything:**
```bash
# Check all equipment (no changes)
python bin/check_data_integrity.py all equipment

# Check all creatures (no changes)
python bin/check_data_integrity.py all creatures
```

**Fix data:**
```bash
# Fix 50 random equipment items
python bin/check_data_integrity.py 50 equipment --replace

# Fix ALL equipment items (WARNING: This will update 3150+ items!)
python bin/check_data_integrity.py all equipment --replace

# Fix ALL creatures
python bin/check_data_integrity.py all creatures --replace
```

## Output

### Check Mode (no --replace)
```
Data Integrity Checker
============================================================
Checking 5 random equipment items

Loaded 3150 items from JSON


[1/5]
Checking: Animal-Turning Fulu
  Our data: Level 0, Price 0 gp, Rarity rare
  Found: Animal-Turning Fulu
  ! Mismatches found:
    - Level: ours=0, AoN=1
    - Price: ours=0 gp, AoN=400

...

============================================================
SUMMARY
============================================================
Total checked: 5
  OK Matches: 0
  ! Mismatches: 5
  X Not found: 0

Accuracy: 0.0%
============================================================
```

### Replace Mode (with --replace)
```
Data Integrity Checker
============================================================
Checking 3 random equipment items
REPLACE MODE: Will update mismatched items with AoN data

Loaded 3150 items from JSON


[1/3]
Checking: Diplomat's Badge
  Our data: Level 0, Price 0 gp, Rarity common
  Found: Diplomat's Badge
  ! Mismatches found:
    - Level: ours=0, AoN=5
    - Price: ours=0 gp, AoN=12500
  >> Updated with AoN data

...

============================================================
SUMMARY
============================================================
Total checked: 3
  OK Matches: 0
  ! Mismatches: 3
  X Not found: 0
  >> Updated: 3

Accuracy: 0.0%
============================================================

Saving updated data to etc/equipment.json...
Saved! 3 items updated.
```

## How It Works

1. **Search**: Queries AoN's Elasticsearch API at `https://elasticsearch.aonprd.com/aon/_search`
2. **Compare**: Compares the API response data with your JSON files
3. **Update** (if --replace): Replaces incorrect data with AoN data
4. **Save** (if --replace): Writes updated JSON back to file

## Performance

- Fast: ~0.5 seconds per item
- Reliable: Uses official API, no rate limiting
- Accurate: Direct access to AoN's database
- Safe: Creates backup before modifying (recommended to use git)

## Recommendations

1. **Test first**: Run without `--replace` to see what will change
2. **Start small**: Fix a sample before running `all --replace`
3. **Use git**: Commit before running replace mode so you can revert if needed
4. **Verify**: Check a few items after replacement to ensure quality

## Key Findings

Testing reveals that **your equipment.json has major data quality issues**:
- Most items show `level: 0` (should be 1-20)
- Most items show `price: "0 gp"` or incorrect prices
- The data needs to be refreshed from AoN

**Solution**: Run `python bin/check_data_integrity.py all equipment --replace` to fix everything!

## Credit

Thanks to [Luke Parke's article](https://dev.to/lukeparke/scraping-archives-of-nethys-for-fun-and-profit-3ll3) for discovering the Elasticsearch API!
