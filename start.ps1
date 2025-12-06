Write-Host "===============================" -ForegroundColor Cyan
Write-Host "🚀 Iniciando OSSO BOT SYSTEM..." -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Cyan

# Detectar caminho do projeto
$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "Caminho detectado: $projectPath" -ForegroundColor Yellow

# Ativar ambiente virtual (caso exista)
$venvPath = Join-Path $projectPath "venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Ativando ambiente virtual..." -ForegroundColor Green
    & $venvPath
} else {
    Write-Host "⚠️ Ambiente virtual não encontrado! Execute 'python -m venv venv' e tente novamente." -ForegroundColor Red
    exit
}

# Iniciar servidor Flask diretamente no terminal
Write-Host "Iniciando servidor Flask (porta 5000)..." -ForegroundColor Cyan
python osso_api.py
