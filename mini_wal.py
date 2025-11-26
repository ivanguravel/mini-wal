import os
import sys
import time
import zlib  # for CRC32

DB_FILE = "db.txt"
WAL_FILE = "wal.log"

def append_wal(entry: str):
    """Append an entry to the WAL with CRC and fsync"""
    crc = zlib.crc32(entry.encode())
    line = f"{crc:08x}|{entry}\n"
    with open(WAL_FILE, "a") as f:
        f.write(line)
        f.flush()
        os.fsync(f.fileno())
    print(f"Appended to WAL: {entry} (crc={crc:08x})")

def commit():
    """Atomically apply WAL to the database and clear WAL"""
    tmp_db = DB_FILE + ".tmp"

    # read current DB content
    db_content = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            db_content = f.read()

    # read WAL and verify CRC
    wal_content = ""
    if os.path.exists(WAL_FILE):
        with open(WAL_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    crc_str, entry = line.split("|", 1)
                    crc_val = int(crc_str, 16)
                    if crc_val != zlib.crc32(entry.encode()):
                        print(f"WARNING: WAL corrupted line skipped: {line}")
                        continue  # skip corrupted line
                    wal_content += entry + "\n"
                except Exception:
                    print(f"WARNING: WAL corrupted line skipped: {line}")
                    continue

    # write all to temporary DB file
    with open(tmp_db, "w") as f:
        f.write(db_content)
        f.write(wal_content)
        f.flush()
        os.fsync(f.fileno())

    # atomically replace DB
    os.rename(tmp_db, DB_FILE)

    # remove WAL after successful commit
    os.remove(WAL_FILE)
    print("Commit finished, WAL cleared.")

if __name__ == "__main__":
    # if "recover" argument is passed, recover from WAL
    if len(sys.argv) > 1 and sys.argv[1] == "recover":
        if os.path.exists(WAL_FILE):
            print("Recovering WAL...")
            commit()
        else:
            print("No WAL to recover.")
        sys.exit(0)

    # normal operation: append entries with delay
    for i in range(1000):
        append_wal(f"SET key{i}={i}")
        time.sleep(0.01)