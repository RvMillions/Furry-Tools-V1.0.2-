# Setup-FurryTools.ps1
$BarWidth = 40

function Show-ProgressBar {
    param(
        [int]$Percent,
        [string]$Step = "Progression"
    )
    $filled = [math]::Round($Percent * $BarWidth / 100)
    $empty = $BarWidth - $filled
    $bar = ("█" * $filled) + ("░" * $empty)
    Write-Host -NoNewline "`r[$bar] $Percent% - $Step"
    if ($Percent -eq 100) { Write-Host "" }
}

Clear-Host
Show-ProgressBar 0 "Vérification de Python 3.10..."

# Vérifier Python 3.10
$PythonOK = $false
try {
    $pyver = & python --version 2>&1
    if ($pyver -match "Python 3\.10") { $PythonOK = $true }
} catch {}

if ($PythonOK) {
    Show-ProgressBar 10 "Python $pyver trouvé, OK."
} else {
    Show-ProgressBar 10 "Python 3.10 non trouvé, téléchargement nécessaire..."
    
    # Détection architecture
    if ($env:PROCESSOR_ARCHITECTURE -eq "AMD64") { $arch = "amd64" } else { $arch = "win32" }
    $PythonURL = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-$arch.exe"
    $Installer = "$env:TEMP\python-3.10.11-$arch.exe"

    Show-ProgressBar 20 "Téléchargement de Python 3.10..."
    Invoke-WebRequest -Uri $PythonURL -OutFile $Installer -UseBasicParsing -Verbose:$false

    Show-ProgressBar 40 "Téléchargement terminé."

    Show-ProgressBar 50 "Installation de Python (silencieuse)..."
    Start-Process -FilePath $Installer -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_test=0" -Wait

    Remove-Item $Installer -Force
    Show-ProgressBar 60 "Python 3.10 installé."
}

# Installer les dépendances
Show-ProgressBar 70 "Installation des dépendances (requirements.txt)..."
if (-Not (Test-Path "requirements.txt")) {
    Write-Host "`n[ERREUR] requirements.txt introuvable."
    exit 1
}

# Mettre à jour pip et installer les packages
& python -m pip install --upgrade pip | Out-Null
& python -m pip install -r requirements.txt | Out-Null
Show-ProgressBar 85 "Dépendances installées."

# Lancer l'application
Show-ProgressBar 95 "Lancement de Furry Tools..."
if (-Not (Test-Path "launch.vbs")) {
    Write-Host "`n[ERREUR] launch.vbs introuvable."
    exit 1
}
Start-Process "wscript.exe" "launch.vbs"
Show-ProgressBar 100 "Installation terminée avec succès !"

Write-Host "`nL'application a été lancée en arrière-plan."
Start-Sleep -Seconds 3