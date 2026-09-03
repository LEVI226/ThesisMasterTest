# backup_thesis.ps1 — Sauvegarde les fichiers locaux NON versionnés (Windows)
# À lancer depuis le dossier du projet :  powershell -ExecutionPolicy Bypass -File .\backup_thesis.ps1
# Crée thesis_backup.zip sur le Bureau, contenant .env + storage\ (uploads + base vectorielle)

$ErrorActionPreference = "Stop"
$projet  = $PSScriptRoot
$bureau  = [Environment]::GetFolderPath("Desktop")
$sortie  = Join-Path $bureau "thesis_backup.zip"

Write-Host "Projet  : $projet"
Write-Host "Archive : $sortie"

$aZipper = @()
foreach ($item in @(".env", "storage")) {
    $p = Join-Path $projet $item
    if (Test-Path $p) { $aZipper += $p } else { Write-Warning "Introuvable, ignoré : $item" }
}

if (Test-Path $sortie) { Remove-Item $sortie -Force }
Compress-Archive -Path $aZipper -DestinationPath $sortie -CompressionLevel Fastest

$taille = "{0:N1} Mo" -f ((Get-Item $sortie).Length / 1MB)
Write-Host "OK — sauvegarde créée ($taille). Copiez ce fichier sur une clé USB ou un cloud." -ForegroundColor Green
