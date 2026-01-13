import os
import sys
import time
import json
import logging
# Ensure project root is in sys.path so `src` package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.utils.logger import setup_global_logging

# Load config
cfg_path = os.path.join('src', 'config', 'config.json')
with open(cfg_path, 'r', encoding='utf-8') as f:
    cfg = json.load(f)

log_file = cfg.get('log_file')
log_dir = os.path.dirname(log_file)

# Ensure log directory exists
os.makedirs(log_dir, exist_ok=True)

# Clean up existing log files for a clean test
for fname in os.listdir(log_dir):
    if fname.startswith(os.path.basename(log_file)):
        try:
            os.remove(os.path.join(log_dir, fname))
        except Exception as e:
            print('Warning: could not remove', fname, e)

# Setup logging according to config
setup_global_logging(cfg)
logger = logging.getLogger('rotation_test')

# Print handler details
rot_handler = None
for h in logging.root.handlers:
    if isinstance(h, logging.handlers.RotatingFileHandler):
        rot_handler = h
        break

print('Rotating Handler:', bool(rot_handler))
if rot_handler:
    print('baseFilename:', getattr(rot_handler, 'baseFilename', None))
    print('maxBytes:', getattr(rot_handler, 'maxBytes', None))
    print('backupCount:', getattr(rot_handler, 'backupCount', None))

# Generate logs until rotation detected (or until target backup index appears)
msg = 'X' * 2000  # ~2KB per message
i = 0
# target backup index to detect (e.g., 3 means we expect app.log.3 to appear)
target_backup = 3
rotation_reached = False
while i < 500000:
    logger.info(f"{i} {msg}")
    i += 1
    if i % 50 == 0:
        files = sorted(os.listdir(log_dir))
        # determine highest numeric backup index present
        backups = [f for f in files if f.startswith(os.path.basename(log_file) + '.')]
        max_index = 0
        for b in backups:
            try:
                idx = int(b.split('.')[-1])
                if idx > max_index:
                    max_index = idx
            except Exception:
                continue
        sizes = {f: os.path.getsize(os.path.join(log_dir, f)) for f in files}
        print('iter', i, 'files', files, 'max_backup_index', max_index, 'sizes', sizes)
        if max_index >= target_backup:
            rotation_reached = True
            print(f'Rotation reached target (>= {target_backup}) at iter', i)
            break

if not rotation_reached:
    print('Rotation target not reached after', i, 'messages')

# Final listing
files = sorted(os.listdir(log_dir))
sizes = {f: os.path.getsize(os.path.join(log_dir, f)) for f in files}
print('Final files:', files)
print('Final sizes:', sizes)

# Verify backup count
expected_backup = cfg.get('backup_count')
actual_backups = len([f for f in files if f != os.path.basename(log_file)])
print('expected_backup:', expected_backup, 'actual_backup_files:', actual_backups)

# Show sample of log lines from base and backup if present
print('\n--- tail of base log ---')
with open(os.path.join(log_dir, os.path.basename(log_file)), 'rb') as f:
    f.seek(max(0, os.path.getsize(os.path.join(log_dir, os.path.basename(log_file))) - 1000))
    print(f.read().decode('utf-8', errors='ignore'))

for f in files:
    if f.endswith('.1'):
        print('\n--- head of backup', f, '---')
        with open(os.path.join(log_dir, f), 'rb') as bf:
            print(bf.read(500).decode('utf-8', errors='ignore'))
        break
