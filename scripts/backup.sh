#!/usr/bin/env bash

set -Eeuo pipefail

umask 077

PROJECT_DIR="${PROJECT_DIR:-/srv/neo-portfolio}"
BACKUP_DIR="${BACKUP_DIR:-/srv/backups/neo-portfolio}"
BACKUP_BUCKET="${BACKUP_BUCKET:-neo-portfolio-backups}"
BACKUP_PREFIX="${BACKUP_PREFIX:-daily}"
LOCAL_RETENTION_DAYS="${LOCAL_RETENTION_DAYS:-14}"
OCI_CLI="${OCI_CLI:-/home/ubuntu/bin/oci}"
PYTHON="${PYTHON:-${PROJECT_DIR}/.venv/bin/python}"

mkdir -p "${BACKUP_DIR}"

PROJECT_DIR="$(realpath -e "${PROJECT_DIR}")"
BACKUP_DIR="$(realpath -e "${BACKUP_DIR}")"

if [[ "${BACKUP_DIR}" == "/" ]]; then
    echo "Refusing to use the filesystem root as BACKUP_DIR." >&2
    exit 1
fi

exec 9>"${BACKUP_DIR}/.backup.lock"
if ! flock -n 9; then
    echo "Another Neo Portfolio backup is already running." >&2
    exit 1
fi

backup_stamp="$(date -u +%Y-%m-%d_%H-%M-%S)"
archive_name="neo-portfolio_${backup_stamp}.tar.gz"
archive_path="${BACKUP_DIR}/${archive_name}"
partial_archive="${archive_path}.partial"
checksum_name="${archive_name}.sha256"
checksum_path="${BACKUP_DIR}/${checksum_name}"
work_dir="$(mktemp -d "${BACKUP_DIR}/.backup-${backup_stamp}-XXXXXX")"

case "${work_dir}" in
    "${BACKUP_DIR}"/.backup-*) ;;
    *)
        echo "Temporary backup path is outside BACKUP_DIR." >&2
        exit 1
        ;;
esac

cleanup() {
    rm -rf -- "${work_dir}"
    rm -f -- "${partial_archive}"
}

trap cleanup EXIT

cd "${PROJECT_DIR}"

"${PYTHON}" - "${work_dir}/db.sqlite3" <<'PY'
import sqlite3
import sys
from pathlib import Path


destination_path = sys.argv[1]
source_path = Path("db.sqlite3").resolve()

if not source_path.is_file():
    raise SystemExit(f"Database does not exist: {source_path}")

with sqlite3.connect(
    f"{source_path.as_uri()}?mode=ro",
    uri=True,
) as source:
    with sqlite3.connect(destination_path) as destination:
        source.backup(destination)
        result = destination.execute("PRAGMA integrity_check").fetchone()[0]

if result != "ok":
    raise SystemExit(f"SQLite integrity check failed: {result}")

print("SQLite backup integrity check: ok")
PY

mkdir -p "${work_dir}/media"
if [[ -d "${PROJECT_DIR}/media" ]]; then
    cp -a "${PROJECT_DIR}/media/." "${work_dir}/media/"
fi

{
    printf 'Created (UTC): %s\n' "$(date -u --iso-8601=seconds)"
    printf 'Git commit: %s\n' "$(git rev-parse HEAD 2>/dev/null || printf 'unknown')"
    printf 'Contents: db.sqlite3, media/\n'
} > "${work_dir}/BACKUP_INFO.txt"

tar -czf "${partial_archive}" \
    -C "${work_dir}" \
    db.sqlite3 media BACKUP_INFO.txt

tar -tzf "${partial_archive}" >/dev/null
mv "${partial_archive}" "${archive_path}"

(
    cd "${BACKUP_DIR}"
    sha256sum "${archive_name}" > "${checksum_name}"
)

"${OCI_CLI}" os object put \
    --bucket-name "${BACKUP_BUCKET}" \
    --name "${BACKUP_PREFIX}/${archive_name}" \
    --file "${archive_path}" \
    --auth instance_principal \
    --force

"${OCI_CLI}" os object put \
    --bucket-name "${BACKUP_BUCKET}" \
    --name "${BACKUP_PREFIX}/${checksum_name}" \
    --file "${checksum_path}" \
    --auth instance_principal \
    --force

find "${BACKUP_DIR}" \
    -maxdepth 1 \
    -type f \
    -name 'neo-portfolio_[0-9][0-9][0-9][0-9]-*.tar.gz' \
    -mtime +"${LOCAL_RETENTION_DAYS}" \
    -print \
    -delete

find "${BACKUP_DIR}" \
    -maxdepth 1 \
    -type f \
    -name 'neo-portfolio_[0-9][0-9][0-9][0-9]-*.tar.gz.sha256' \
    -mtime +"${LOCAL_RETENTION_DAYS}" \
    -print \
    -delete

echo "Created local backup: ${archive_path}"
echo "Created checksum: ${checksum_path}"
echo "Uploaded Object Storage backup: ${BACKUP_PREFIX}/${archive_name}"
