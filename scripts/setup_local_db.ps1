# One-time local PostgreSQL setup for ProductFlow verification.
# Creates role/database matching .env.example, then restores pg_hba.conf.

$ErrorActionPreference = "Stop"
$PgBin = "C:\Program Files\PostgreSQL\18\bin"
$PgData = "C:\Program Files\PostgreSQL\18\data"
$PgHba = Join-Path $PgData "pg_hba.conf"
$Backup = Join-Path $PgData "pg_hba.conf.productflow.bak"

if (-not (Test-Path $Backup)) {
    Copy-Item $PgHba $Backup
}

$content = Get-Content $PgHba -Raw
$content = $content -replace "127\.0\.0\.1/32\s+scram-sha-256", "127.0.0.1/32            trust"
$content = $content -replace "::1/128\s+scram-sha-256", "::1/128                 trust"
Set-Content -Path $PgHba -Value $content -NoNewline

& "$PgBin\pg_ctl.exe" reload -D $PgData
Start-Sleep -Seconds 2

& "$PgBin\psql.exe" -U postgres -h 127.0.0.1 -d postgres -v ON_ERROR_STOP=0 -c "CREATE ROLE productflow LOGIN PASSWORD 'productflow';"
& "$PgBin\psql.exe" -U postgres -h 127.0.0.1 -d postgres -v ON_ERROR_STOP=0 -c "CREATE DATABASE productflow OWNER productflow;"
& "$PgBin\psql.exe" -U postgres -h 127.0.0.1 -d postgres -v ON_ERROR_STOP=1 -c "GRANT ALL PRIVILEGES ON DATABASE productflow TO productflow;"

Copy-Item $Backup $PgHba -Force
& "$PgBin\pg_ctl.exe" reload -D $PgData

Write-Host "PostgreSQL role/database 'productflow' ready."
