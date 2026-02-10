#!/usr/bin/env python3
"""
File organization utilities: duplicate detection, smart organization, cleanup.
"""

import os
import shutil
import hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import json

class FileOrganizer:
    
    # Common file type categories
    FILE_CATEGORIES = {
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.odt', '.rtf', '.tex'],
        'spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
        'presentations': ['.ppt', '.pptx', '.key', '.odp'],
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'],
        'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
        'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
        'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
        'code': ['.py', '.js', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go', '.rs'],
        'web': ['.html', '.css', '.scss', '.sass', '.less'],
        'data': ['.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg'],
        'executables': ['.exe', '.msi', '.app', '.dmg', '.deb', '.rpm'],
        'fonts': ['.ttf', '.otf', '.woff', '.woff2']
    }
    
    def __init__(self, base_path='.'):
        self.base_path = Path(base_path).resolve()
    
    # ===== Duplicate Detection =====
    
    def find_duplicates(self, directory=None, min_size=1024):
        """
        Find duplicate files by comparing file hashes.
        
        Args:
            directory: Directory to scan (default: base_path)
            min_size: Minimum file size in bytes to consider (default: 1KB)
        
        Returns:
            Dict of {hash: [file_paths]} for duplicates
        """
        directory = Path(directory or self.base_path)
        
        # Group files by size first (fast pre-filter)
        size_map = defaultdict(list)
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                try:
                    size = file_path.stat().st_size
                    if size >= min_size:
                        size_map[size].append(file_path)
                except (PermissionError, OSError):
                    continue
        
        # Hash files with same size
        hash_map = defaultdict(list)
        
        for size, files in size_map.items():
            if len(files) > 1:
                for file_path in files:
                    try:
                        file_hash = self._hash_file(file_path)
                        hash_map[file_hash].append(str(file_path))
                    except (PermissionError, OSError):
                        continue
        
        # Return only actual duplicates
        duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
        
        return duplicates
    
    def _hash_file(self, file_path, chunk_size=8192):
        """Calculate MD5 hash of file."""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def remove_duplicates(self, duplicates, keep='first', dry_run=True):
        """
        Remove duplicate files, keeping one copy.
        
        Args:
            duplicates: Dict from find_duplicates()
            keep: 'first', 'last', 'shortest_path', 'longest_path'
            dry_run: If True, only report what would be deleted
        
        Returns:
            List of deleted (or would-be-deleted) file paths
        """
        deleted = []
        
        for file_hash, paths in duplicates.items():
            # Decide which to keep
            if keep == 'first':
                to_keep = paths[0]
            elif keep == 'last':
                to_keep = paths[-1]
            elif keep == 'shortest_path':
                to_keep = min(paths, key=len)
            elif keep == 'longest_path':
                to_keep = max(paths, key=len)
            else:
                raise ValueError(f"Invalid keep strategy: {keep}")
            
            # Delete the rest
            for path in paths:
                if path != to_keep:
                    if not dry_run:
                        try:
                            os.remove(path)
                        except (PermissionError, OSError) as e:
                            print(f"Failed to delete {path}: {e}")
                            continue
                    deleted.append(path)
        
        return deleted
    
    # ===== Smart Organization =====
    
    def organize_by_type(self, source_dir=None, dest_dir=None, dry_run=True):
        """
        Organize files into category folders by file type.
        
        Args:
            source_dir: Source directory (default: base_path)
            dest_dir: Destination directory (default: source_dir/organized)
            dry_run: If True, only report what would be done
        
        Returns:
            Dict of moves: {source: destination}
        """
        source_dir = Path(source_dir or self.base_path)
        dest_dir = Path(dest_dir or source_dir / 'organized')
        
        moves = {}
        
        for file_path in source_dir.iterdir():
            if file_path.is_file():
                category = self._get_category(file_path.suffix.lower())
                
                if category:
                    dest_path = dest_dir / category / file_path.name
                    moves[str(file_path)] = str(dest_path)
                    
                    if not dry_run:
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(file_path), str(dest_path))
        
        return moves
    
    def organize_by_date(self, source_dir=None, dest_dir=None, date_format='%Y/%m', dry_run=True):
        """
        Organize files into date-based folders.
        
        Args:
            source_dir: Source directory
            dest_dir: Destination directory
            date_format: strftime format for folder structure (default: YYYY/MM)
            dry_run: If True, only report what would be done
        
        Returns:
            Dict of moves: {source: destination}
        """
        source_dir = Path(source_dir or self.base_path)
        dest_dir = Path(dest_dir or source_dir / 'organized')
        
        moves = {}
        
        for file_path in source_dir.rglob('*'):
            if file_path.is_file():
                try:
                    # Use modification time
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    date_folder = mtime.strftime(date_format)
                    
                    dest_path = dest_dir / date_folder / file_path.name
                    moves[str(file_path)] = str(dest_path)
                    
                    if not dry_run:
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(file_path), str(dest_path))
                except (PermissionError, OSError):
                    continue
        
        return moves
    
    def _get_category(self, extension):
        """Get file category from extension."""
        for category, extensions in self.FILE_CATEGORIES.items():
            if extension in extensions:
                return category
        return 'other'
    
    # ===== Cleanup =====
    
    def find_empty_dirs(self, directory=None):
        """Find all empty directories."""
        directory = Path(directory or self.base_path)
        empty_dirs = []
        
        for dir_path in directory.rglob('*'):
            if dir_path.is_dir():
                try:
                    if not any(dir_path.iterdir()):
                        empty_dirs.append(str(dir_path))
                except (PermissionError, OSError):
                    continue
        
        return empty_dirs
    
    def remove_empty_dirs(self, directory=None, dry_run=True):
        """Remove all empty directories."""
        empty_dirs = self.find_empty_dirs(directory)
        
        if not dry_run:
            for dir_path in empty_dirs:
                try:
                    os.rmdir(dir_path)
                except (PermissionError, OSError):
                    pass
        
        return empty_dirs
    
    def find_temp_files(self, directory=None):
        """
        Find temporary files (common patterns).
        
        Patterns: ~*, .tmp, .temp, .cache, .bak, .old, Desktop.ini, Thumbs.db, .DS_Store
        """
        directory = Path(directory or self.base_path)
        temp_patterns = ['~*', '*.tmp', '*.temp', '*.cache', '*.bak', '*.old', 
                        'Desktop.ini', 'Thumbs.db', '.DS_Store', '*.swp', '*.swo']
        
        temp_files = []
        
        for pattern in temp_patterns:
            temp_files.extend(str(p) for p in directory.rglob(pattern) if p.is_file())
        
        return temp_files
    
    def remove_temp_files(self, directory=None, dry_run=True):
        """Remove temporary files."""
        temp_files = self.find_temp_files(directory)
        
        if not dry_run:
            for file_path in temp_files:
                try:
                    os.remove(file_path)
                except (PermissionError, OSError):
                    pass
        
        return temp_files
    
    def find_old_files(self, directory=None, days=30):
        """Find files older than specified days."""
        directory = Path(directory or self.base_path)
        cutoff = datetime.now().timestamp() - (days * 86400)
        old_files = []
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                try:
                    if file_path.stat().st_mtime < cutoff:
                        old_files.append(str(file_path))
                except (PermissionError, OSError):
                    continue
        
        return old_files
    
    # ===== Analysis =====
    
    def analyze_disk_usage(self, directory=None, top_n=10):
        """
        Analyze disk usage by file type and large files.
        
        Returns:
            Dict with type_breakdown, largest_files, total_size
        """
        directory = Path(directory or self.base_path)
        
        type_sizes = defaultdict(int)
        file_sizes = []
        total_size = 0
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                try:
                    size = file_path.stat().st_size
                    total_size += size
                    
                    ext = file_path.suffix.lower()
                    category = self._get_category(ext)
                    type_sizes[category] += size
                    
                    file_sizes.append((size, str(file_path)))
                except (PermissionError, OSError):
                    continue
        
        # Sort and get top files
        file_sizes.sort(reverse=True)
        largest_files = [
            {'path': path, 'size': size, 'size_mb': round(size / 1024 / 1024, 2)}
            for size, path in file_sizes[:top_n]
        ]
        
        # Format type breakdown
        type_breakdown = {
            cat: {'size': size, 'size_mb': round(size / 1024 / 1024, 2)}
            for cat, size in sorted(type_sizes.items(), key=lambda x: x[1], reverse=True)
        }
        
        return {
            'total_size': total_size,
            'total_size_gb': round(total_size / 1024 / 1024 / 1024, 2),
            'type_breakdown': type_breakdown,
            'largest_files': largest_files
        }
    
    def generate_report(self, output_path='file_report.json'):
        """Generate comprehensive file organization report."""
        report = {
            'generated_at': datetime.now().isoformat(),
            'base_path': str(self.base_path),
            'disk_usage': self.analyze_disk_usage(),
            'duplicates': {h: paths for h, paths in self.find_duplicates().items()},
            'empty_directories': self.find_empty_dirs(),
            'temp_files': self.find_temp_files()
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report


if __name__ == '__main__':
    import sys
    
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    organizer = FileOrganizer(path)
    
    print(f"Analyzing: {organizer.base_path}\n")
    
    # Disk usage
    usage = organizer.analyze_disk_usage()
    print(f"Total size: {usage['total_size_gb']} GB\n")
    
    print("Top file types:")
    for cat, info in list(usage['type_breakdown'].items())[:5]:
        print(f"  {cat}: {info['size_mb']} MB")
    
    print(f"\nLargest files:")
    for file_info in usage['largest_files'][:5]:
        print(f"  {file_info['size_mb']} MB - {file_info['path']}")
    
    # Duplicates
    duplicates = organizer.find_duplicates()
    if duplicates:
        print(f"\nFound {len(duplicates)} sets of duplicate files")
    
    # Temp files
    temp = organizer.find_temp_files()
    if temp:
        print(f"\nFound {len(temp)} temporary files")
