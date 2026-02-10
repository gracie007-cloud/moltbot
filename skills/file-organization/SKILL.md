---
name: file-organization
description: Smart file organization utilities including duplicate detection and removal, automated organization by type or date, cleanup of temporary and old files, empty directory management, and disk usage analysis. Use when tasks involve organizing messy directories, finding/removing duplicates, cleaning up disk space, analyzing file storage, or automating file management workflows.
---

# File Organization

Utilities for smart file organization, duplicate detection, cleanup, and disk usage analysis.

## Quick Start

```python
from scripts.file_organizer import FileOrganizer

# Initialize with directory
org = FileOrganizer('/path/to/directory')

# Find duplicates
duplicates = org.find_duplicates()

# Organize files by type
moves = org.organize_by_type(dry_run=True)  # dry_run to preview

# Analyze disk usage
usage = org.analyze_disk_usage()
```

## Duplicate Detection

### Find Duplicates

```python
# Find all duplicates (min 1KB)
duplicates = org.find_duplicates()

# Custom minimum size (10MB)
duplicates = org.find_duplicates(min_size=10*1024*1024)

# Specific directory
duplicates = org.find_duplicates(directory='/path/to/scan')

# Result format: {hash: [file_paths]}
for file_hash, paths in duplicates.items():
    print(f"Duplicate set ({len(paths)} files):")
    for path in paths:
        print(f"  {path}")
```

### Remove Duplicates

```python
# Preview what would be deleted
deleted = org.remove_duplicates(duplicates, keep='first', dry_run=True)
print(f"Would delete {len(deleted)} files")

# Actually delete (keep first occurrence)
deleted = org.remove_duplicates(duplicates, keep='first', dry_run=False)

# Keep strategies:
# - 'first': Keep first file in list
# - 'last': Keep last file
# - 'shortest_path': Keep file with shortest path
# - 'longest_path': Keep file with longest path
```

## Smart Organization

### Organize by File Type

Automatically categorizes files into folders:

- documents: PDF, DOC, DOCX, TXT, etc.
- images: JPG, PNG, GIF, etc.
- videos: MP4, AVI, MKV, etc.
- code: PY, JS, JAVA, etc.
- archives: ZIP, RAR, 7Z, etc.

```python
# Preview organization
moves = org.organize_by_type(
    source_dir='/path/to/messy',
    dest_dir='/path/to/organized',
    dry_run=True
)

print(f"Would move {len(moves)} files")
for src, dest in list(moves.items())[:5]:
    print(f"{src} -> {dest}")

# Actually organize
moves = org.organize_by_type(dry_run=False)
```

### Organize by Date

```python
# Organize into YYYY/MM folders
moves = org.organize_by_date(
    source_dir='/path/to/files',
    date_format='%Y/%m',  # 2024/02
    dry_run=True
)

# Different date format: YYYY-MM-DD
moves = org.organize_by_date(date_format='%Y-%m-%d', dry_run=False)

# Year only
moves = org.organize_by_date(date_format='%Y', dry_run=False)
```

## Cleanup Operations

### Find and Remove Temp Files

Finds common temporary file patterns:

- Backup files: ~_, _.bak, \*.old
- Temp files: _.tmp, _.temp, \*.cache
- System files: Desktop.ini, Thumbs.db, .DS_Store
- Vim swap: _.swp, _.swo

```python
# Find temp files
temp_files = org.find_temp_files()
print(f"Found {len(temp_files)} temporary files")

# Remove them (preview first)
removed = org.remove_temp_files(dry_run=True)

# Actually remove
removed = org.remove_temp_files(dry_run=False)
print(f"Removed {len(removed)} temp files")
```

### Find and Remove Empty Directories

```python
# Find empty directories
empty_dirs = org.find_empty_dirs()
print(f"Found {len(empty_dirs)} empty directories")

# Remove them
removed = org.remove_empty_dirs(dry_run=False)
```

### Find Old Files

```python
# Files older than 30 days
old_files = org.find_old_files(days=30)

# Files older than 1 year
old_files = org.find_old_files(days=365)

print(f"Found {len(old_files)} old files")
for path in old_files[:10]:
    print(f"  {path}")

# Delete old files manually
import os
for path in old_files:
    os.remove(path)  # Be careful!
```

## Disk Usage Analysis

### Analyze Disk Usage

```python
usage = org.analyze_disk_usage(top_n=10)

# Total size
print(f"Total: {usage['total_size_gb']} GB")

# Breakdown by file type
print("\nFile type breakdown:")
for category, info in usage['type_breakdown'].items():
    print(f"  {category}: {info['size_mb']} MB")

# Largest files
print("\nLargest files:")
for file_info in usage['largest_files']:
    print(f"  {file_info['size_mb']} MB - {file_info['path']}")
```

### Generate Full Report

```python
# Generate JSON report
report = org.generate_report('file_report.json')

# Report includes:
# - Disk usage analysis
# - Duplicate files
# - Empty directories
# - Temporary files
```

## Common Workflows

### Clean Up Downloads Folder

```python
org = FileOrganizer('~/Downloads')

# 1. Remove temp files
temp = org.remove_temp_files(dry_run=False)
print(f"Removed {len(temp)} temp files")

# 2. Organize by type
moves = org.organize_by_type(dest_dir='~/Downloads/organized', dry_run=False)
print(f"Organized {len(moves)} files")

# 3. Find duplicates
duplicates = org.find_duplicates()
if duplicates:
    deleted = org.remove_duplicates(duplicates, keep='first', dry_run=False)
    print(f"Removed {len(deleted)} duplicate files")

# 4. Remove empty folders
empty = org.remove_empty_dirs(dry_run=False)
print(f"Removed {len(empty)} empty directories")
```

### Free Up Disk Space

```python
org = FileOrganizer('/path/to/directory')

# 1. Find largest files
usage = org.analyze_disk_usage(top_n=20)
print("Largest files:")
for file_info in usage['largest_files']:
    print(f"  {file_info['size_mb']} MB - {file_info['path']}")

# 2. Find duplicates
duplicates = org.find_duplicates()
if duplicates:
    print(f"\nFound {len(duplicates)} sets of duplicates")
    # Review and delete manually or automatically

# 3. Find old files
old_files = org.find_old_files(days=180)
print(f"\nFound {len(old_files)} files older than 6 months")
```

### Organize Project Files

```python
org = FileOrganizer('/path/to/project')

# Organize code by type
moves = org.organize_by_type(
    source_dir='/path/to/project/messy',
    dest_dir='/path/to/project/organized',
    dry_run=False
)

# Remove temp files
org.remove_temp_files(dry_run=False)

# Find empty directories after organization
empty = org.find_empty_dirs()
```

## File Categories

Files are organized into these categories:

- **documents**: PDF, DOC, DOCX, TXT, ODT, RTF, TEX
- **spreadsheets**: XLS, XLSX, CSV, ODS
- **presentations**: PPT, PPTX, KEY, ODP
- **images**: JPG, PNG, GIF, BMP, SVG, WEBP, ICO
- **videos**: MP4, AVI, MKV, MOV, WMV, FLV, WEBM
- **audio**: MP3, WAV, FLAC, AAC, OGG, WMA, M4A
- **archives**: ZIP, RAR, 7Z, TAR, GZ, BZ2
- **code**: PY, JS, JAVA, CPP, C, H, CS, PHP, RB, GO, RS
- **web**: HTML, CSS, SCSS, SASS, LESS
- **data**: JSON, XML, YAML, YML, TOML, INI, CFG
- **executables**: EXE, MSI, APP, DMG, DEB, RPM
- **fonts**: TTF, OTF, WOFF, WOFF2
- **other**: Everything else

## Tips & Best Practices

1. **Always use dry_run=True first** to preview changes
2. **Backup important data** before bulk operations
3. **Start with analysis** (analyze_disk_usage, find_duplicates) before acting
4. **Review duplicate lists** before automatic deletion
5. **Test on small directories** before applying to large ones
6. **Use keep='shortest_path'** for duplicates to keep files closer to root
7. **Combine operations** for thorough cleanup (temp + duplicates + empty dirs)

## Safety Notes

- Operations that modify files default to `dry_run=True`
- Review dry-run output before setting `dry_run=False`
- Duplicate detection uses MD5 hashes (not just filenames)
- File moves preserve original modification dates
- Empty directories are only removed if truly empty
- Temp file patterns are conservative (won't delete important files)

## Example Scripts

### Full Cleanup Script

```python
from scripts.file_organizer import FileOrganizer

def cleanup_directory(path):
    org = FileOrganizer(path)

    print(f"Cleaning up: {path}\n")

    # Analysis
    print("1. Analyzing disk usage...")
    usage = org.analyze_disk_usage()
    print(f"   Total: {usage['total_size_gb']} GB\n")

    # Temp files
    print("2. Finding temp files...")
    temp = org.find_temp_files()
    print(f"   Found: {len(temp)} files")
    if temp and input("   Remove? (y/n): ").lower() == 'y':
        org.remove_temp_files(dry_run=False)
        print("   Removed!\n")

    # Duplicates
    print("3. Finding duplicates...")
    dups = org.find_duplicates()
    print(f"   Found: {len(dups)} sets")
    if dups and input("   Remove? (y/n): ").lower() == 'y':
        deleted = org.remove_duplicates(dups, keep='shortest_path', dry_run=False)
        print(f"   Removed {len(deleted)} files!\n")

    # Empty dirs
    print("4. Finding empty directories...")
    empty = org.find_empty_dirs()
    print(f"   Found: {len(empty)} directories")
    if empty and input("   Remove? (y/n): ").lower() == 'y':
        org.remove_empty_dirs(dry_run=False)
        print("   Removed!\n")

    print("Cleanup complete!")

cleanup_directory('/path/to/directory')
```

## Dependencies

No external dependencies - uses Python standard library only.

## Limitations

- Large directories (100k+ files) may take time to scan
- Duplicate detection loads entire files into memory for hashing
- Does not follow symlinks (by design, for safety)
- Requires read/write permissions on target directories
