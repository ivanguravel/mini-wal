# Mini WAL (Write-Ahead Log) Example in Python

This is a simple Python example demonstrating `Write-Ahead Logging (WAL)`**` with:

- Atomic commit using temporary file + rename
- fsync for durability
- CRC32 checks for data integrity

---

## Files

- `mini_wal.py` - main script
- `db.txt` - main database file (will be created during usage)
- `wal.log` - write-ahead log file (will be created during usage)

---

## Usage

### Normal operation

Run the script to append entries to the WAL:

```
python3 mini_wal.py
```
### Simulate crash

You can simulate a crash by killing the script process:

```
python3 mini_wal.py & sleep 1; pkill -9 -f "python.*mini_wal.py"
```

After this:

- `db.txt` may be empty or partially updated
- `wal.log` contains all uncommitted entries that were not yet applied to the DB.
- No data is lost as long as it is in WAL and CRC is valid.

This demonstrates that write operations in WAL are durable, even if the process crashes mid-write.

### Recover from WAL

To apply WAL entries to the main database atomically:

```
python3 mini_wal.py recover
```

All valid entries from WAL are applied to `db.txt`:
- Corrupted entries (CRC mismatch) are skipped
- WAL file is cleared after successful commit
- After recovery, the database contains all committed operations, showing crash recovery in action.

`How it works`

1) Append to WAL: every operation is written to wal.log with a CRC32 checksum.
2) fsync: ensures WAL data is actually written to disk.
3) Commit: read WAL, verify CRC, apply entries to a temporary DB file.
3) Atomic rename: replace main DB file with temporary file.
4) Clear WAL: after successful commit, WAL is deleted.

After this procedure you may verify content of the `db.txt`. It contains all WAL entries applied safely and atomically.

