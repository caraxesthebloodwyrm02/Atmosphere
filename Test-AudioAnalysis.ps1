# Simple test script for audio analysis functionality

# Create test directory
$testDir = ".\test_audio_analysis"
New-Item -ItemType Directory -Path $testDir -Force | Out-Null

# Copy test files to the test directory
Copy-Item -Path ".\test_audio\*" -Destination $testDir -Recurse -Force

# Import the Audio module
$modulePath = ".\automation\modules\Audio"
Import-Module "$modulePath\Atmosphere.Audio.psd1" -Force -ErrorAction Stop

# Test 1: List supported formats
Write-Host "`n=== Test 1: Check Supported Formats ===" -ForegroundColor Cyan
$supportedFormats = (Get-Module Atmosphere.Audio).PrivateData['SupportedFormats']
Write-Host "Supported Audio Formats: $($supportedFormats -join ', ')"

# Test 2: Basic file processing
Write-Host "`n=== Test 2: Basic File Processing ===" -ForegroundColor Cyan
$testFile = Get-ChildItem -Path $testDir -Filter "*.wav" | Select-Object -First 1
if ($testFile) {
    Write-Host "Processing test file: $($testFile.FullName)"
    
    # Process the file
    $result = Start-AudioProcessing -InputFile $testFile.FullName -OutputDirectory "$testDir\processed" -Verbose -ErrorAction Stop
    
    if ($result -and $result.Status -eq 'Completed') {
        Write-Host "File processed successfully: $($result.OutputFile)" -ForegroundColor Green
        
        # Test 3: Analyze audio quality
        Write-Host "`n=== Test 3: Analyze Audio Quality ===" -ForegroundColor Cyan
        $analysis = Measure-AudioQuality -InputPath $result.OutputFile -DetailLevel basic -Verbose -ErrorAction Stop
        
        if ($analysis) {
            Write-Host "Analysis completed successfully!" -ForegroundColor Green
            $analysis | Format-List *
            
            # Test 4: Export report
            Write-Host "`n=== Test 4: Export Report ===" -ForegroundColor Cyan
            $reportPath = "$testDir\audio_quality_report.html"
            $analysis | Export-AudioReport -OutputPath $reportPath -Format HTML -OpenAfterExport -ErrorAction Stop
            
            if (Test-Path $reportPath) {
                Write-Host "Report generated successfully: $reportPath" -ForegroundColor Green
                Start-Process $reportPath
            } else {
                Write-Host "Failed to generate report" -ForegroundColor Red
            }
        } else {
            Write-Host "Failed to analyze audio quality" -ForegroundColor Red
        }
    } else {
        Write-Host "Failed to process audio file" -ForegroundColor Red
    }
} else {
    Write-Host "No test files found in $testDir" -ForegroundColor Red
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
