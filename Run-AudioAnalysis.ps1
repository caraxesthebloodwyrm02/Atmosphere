# Import required modules
Import-Module ".\automation\modules\Core\Atmosphere.psm1" -Force
Import-Module ".\automation\modules\Audio\Atmosphere.Audio.psm1" -Force

# Create output directories
$outputDir = ".\audio_analysis_results"
$reportDir = "$outputDir\reports"
$processedDir = "$outputDir\processed"

New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
New-Item -ItemType Directory -Path $processedDir -Force | Out-Null

# Step 1: Process audio files
Write-Host "`n=== Processing Audio Files ===" -ForegroundColor Cyan
$processedFiles = Get-ChildItem -Path ".\test_audio\*.wav" | 
    Start-AudioProcessing -OutputDirectory $processedDir -Normalize -RemoveSilence -Verbose

# Step 2: Analyze audio quality
Write-Host "`n=== Analyzing Audio Quality ===" -ForegroundColor Cyan
$analysisResults = $processedFiles | 
    Where-Object { $_.Status -eq 'Completed' } | 
    Select-Object -ExpandProperty OutputFile | 
    Measure-AudioQuality -DetailLevel detailed -Verbose

# Step 3: Generate reports
Write-Host "`n=== Generating Reports ===" -ForegroundColor Cyan
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$htmlReportPath = "$reportDir\audio_quality_report_${timestamp}.html"
$csvReportPath = "$reportDir\audio_quality_data_${timestamp}.csv"

# HTML Report
$analysisResults | Export-AudioReport -OutputPath $htmlReportPath -Format HTML -Title "Audio Quality Analysis Report" -IncludeCharts -OpenAfterExport

# CSV Report for further analysis
$analysisResults | Export-AudioReport -OutputPath $csvReportPath -Format CSV

# Display summary
Write-Host "`n=== Analysis Complete ===" -ForegroundColor Green
Write-Host "Processed Files: $($analysisResults.Count)"
Write-Host "HTML Report: $((Resolve-Path $htmlReportPath).Path)"
Write-Host "CSV Data: $((Resolve-Path $csvReportPath).Path)"

# Display results in console
$analysisResults | Format-Table -Property @(
    @{Name='File'; Expression={$_.FileName}; Width=20},
    @{Name='Quality Score'; Expression={"$([math]::Round($_.Metrics.AudioQualityScore, 1))/100"}; Align='Right'},
    @{Name='Rating'; Expression={
        $color = switch ($_.Metrics.AudioQualityRating) {
            'Excellent' { 'Green' }
            'Good' { 'Cyan' }
            'Average' { 'Yellow' }
            'Poor' { 'Red' }
            default { 'Gray' }
        }
        $rating = $_.Metrics.AudioQualityRating
        "`e[38;5;$((Get-Host).PrivateData.$($color).value)m$rating`e[0m"
    }; Width=15},
    @{Name='Format'; Expression={"$($_.Metrics.Basic.Format.ToUpper()) $($_.Metrics.Basic.SampleRate/1000)kHz $($_.Metrics.Basic.BitDepth)bit"}; Width=25},
    @{Name='Size'; Expression={"$([math]::Round($_.Metrics.FileInfo.FileSize / 1KB, 1)) KB"}; Align='Right'}
) -AutoSize

# Open the HTML report
Start-Process $htmlReportPath
