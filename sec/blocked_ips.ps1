# Block suspicious IPs
$blockedIPs = @(
    "104.18.39.21",
    "4.213.25.240",
    "64.233.170.188",
    "20.195.84.7",
    "34.49.14.144",
    "35.223.238.178",
    "40.99.33.162"
)

foreach ($ip in $blockedIPs) {
    $ruleName = "Block_$($ip.Replace('.', '_'))_Outbound"
    
    # Check if rule already exists
    $existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    
    if (-not $existingRule) {
        try {
            New-NetFirewallRule -DisplayName $ruleName `
                -Direction Outbound `
                -Action Block `
                -RemoteAddress $ip `
                -Profile Any `
                -Enabled True `
                -ErrorAction Stop
            Write-Host "Blocked outbound traffic to $ip" -ForegroundColor Green
        }
        catch {
            Write-Host "Failed to block $ip : $_" -ForegroundColor Red
        }
    } else {
        Write-Host "Rule for $ip already exists" -ForegroundColor Yellow
    }
}

# Verify rules were created
Get-NetFirewallRule -DisplayName "Block_*" | Select-Object DisplayName, Enabled, Direction, Action
