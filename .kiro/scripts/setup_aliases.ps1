# Kiro Commit Buddy - PowerShell Setup
# This script sets up convenient aliases for Kiro Commit Buddy

# Function to run Kiro Commit Buddy
function Invoke-KiroCommit {
    param(
        [switch]$FromDiff,
        [string[]]$Arguments
    )
    
    $scriptPath = Join-Path $PWD ".kiro/scripts/commit_buddy.py"
    
    if (-not (Test-Path $scriptPath)) {
        Write-Error "Kiro Commit Buddy not found at $scriptPath"
        return
    }
    
    $args = @()
    if ($FromDiff) {
        $args += "--from-diff"
    }
    $args += $Arguments
    
    & python $scriptPath @args
}

# Create convenient aliases
Set-Alias -Name kcommit -Value Invoke-KiroCommit
Set-Alias -Name kiro-commit -Value Invoke-KiroCommit

# Export functions for use in other sessions
Export-ModuleMember -Function Invoke-KiroCommit -Alias kcommit, kiro-commit

Write-Host "✅ Kiro Commit Buddy aliases created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "  kcommit -FromDiff          # Generate commit from staged changes" -ForegroundColor White
Write-Host "  kiro-commit -FromDiff      # Same as above" -ForegroundColor White
Write-Host "  Invoke-KiroCommit -FromDiff # Full function name" -ForegroundColor White
Write-Host ""
Write-Host "To make these aliases permanent, add this script to your PowerShell profile:" -ForegroundColor Yellow
Write-Host "  . .kiro/scripts/setup_aliases.ps1" -ForegroundColor White
