# =============================================
# SECURE CLEANUP SCRIPT
# =============================================

# Run this to securely clean up sensitive data
function Clear-SecureWorkspace {
    param(
        [switch]$Shred
    )
    
    $secureItems = Get-ChildItem -Path "E:\SecureWorkspace" -Recurse -File | 
        Where-Object { $_.Extension -in (Get-Content "E:\SecureWorkspace\.secureconfig" | ConvertFrom-Json).ProtectedExtensions }
    
    foreach ($file in $secureItems) {
        if ($Shred) {
            # Overwrite file with random data before deletion
            $size = $file.Length
            $random = New-Object byte[] $size
            $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
            $rng.GetBytes($random)
            [System.IO.File]::WriteAllBytes($file.FullName, $random)
        }
        
        # Secure delete
        Remove-Item $file.FullName -Force -ErrorAction SilentlyContinue
    }
    
    # Clear PowerShell history
    Clear-History
    Remove-Item (Get-PSReadLineOption).HistorySavePath -ErrorAction SilentlyContinue
    
    Write-Host "Secure cleanup completed" -ForegroundColor Green
}

# Add to profile
Set-Alias -Name secure-clean -Value Clear-SecureWorkspace
