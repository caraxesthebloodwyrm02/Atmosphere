# Test script for direct audio analysis

# Create output directory
$outputDir = ".\audio_test_results"
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

# Test files
$testFiles = Get-ChildItem -Path ".\test_audio" -Filter "*.wav" -File

if ($testFiles.Count -eq 0) {
    Write-Host "No test files found in .\test_audio directory" -ForegroundColor Red
    exit 1
}

# Test 1: Check if FFmpeg is available
try {
    $ffmpegVersion = & ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host "FFmpeg version: $ffmpegVersion" -ForegroundColor Green
} catch {
    Write-Host "FFmpeg is not installed or not in PATH. Please install FFmpeg first." -ForegroundColor Red
    exit 1
}

# Test 2: Analyze each test file
$results = @()

foreach ($file in $testFiles) {
    Write-Host "`nAnalyzing $($file.Name)..." -ForegroundColor Cyan
    
    # Get basic file info
    $fileInfo = [PSCustomObject]@{
        FileName = $file.Name
        FilePath = $file.FullName
        FileSize = [math]::Round($file.Length / 1KB, 2)
        LastModified = $file.LastWriteTime
    }
    
    # Get audio info using ffprobe
    $ffprobeCmd = "ffprobe -v error -show_entries format=duration,size,bit_rate:stream=codec_name,sample_rate,channels,bits_per_sample -of json `"$($file.FullName)`""
    $ffprobeOutput = Invoke-Expression $ffprobeCmd | ConvertFrom-Json
    
    # Extract audio metrics
    $metrics = @{
        Basic = @{
            Duration = [math]::Round([double]$ffprobeOutput.format.duration, 2)
            Format = $ffprobeOutput.format.format_name
            Bitrate = [math]::Round([double]$ffprobeOutput.format.bit_rate / 1000, 2)
            SampleRate = [int]$ffprobeOutput.streams[0].sample_rate
            Channels = [int]$ffprobeOutput.streams[0].channels
            BitDepth = [int]$ffprobeOutput.streams[0].bits_per_sample
        }
        FileInfo = @{
            FileSize = [math]::Round($file.Length / 1MB, 2)
            LastModified = $file.LastWriteTime
        }
    }
    
    # Calculate a simple quality score (0-100)
    $qualityScore = 0
    
    # Score based on sample rate (max 30 points)
    $qualityScore += [math]::Min(30, ($metrics.Basic.SampleRate / 44100) * 30)
    
    # Score based on bit depth (max 20 points)
    $qualityScore += [math]::Min(20, ($metrics.Basic.BitDepth / 24) * 20)
    
    # Score based on bitrate (max 30 points, assuming 320kbps is excellent)
    $qualityScore += [math]::Min(30, ($metrics.Basic.Bitrate / 320) * 30)
    
    # Score based on channels (max 20 points, 2 channels = 20 points, 1 channel = 10 points)
    $qualityScore += $metrics.Basic.Channels * 10
    
    # Cap at 100
    $qualityScore = [math]::Min(100, [math]::Round($qualityScore, 2))
    
    # Determine quality rating
    $qualityRating = switch ($qualityScore) {
        {$_ -ge 90} { "Excellent" }
        {$_ -ge 75} { "Good" }
        {$_ -ge 50} { "Average" }
        default { "Poor" }
    }
    
    $metrics.AudioQualityScore = $qualityScore
    $metrics.AudioQualityRating = $qualityRating
    
    # Create result object
    $result = [PSCustomObject]@{
        FileName = $file.Name
        FilePath = $file.FullName
        Status = 'Completed'
        Metrics = $metrics
    }
    
    $results += $result
    
    # Display results
    Write-Host "  Format: $($metrics.Basic.Format.ToUpper()) $($metrics.Basic.SampleRate/1000)kHz $($metrics.Basic.BitDepth)bit"
    Write-Host "  Channels: $($metrics.Basic.Channels)"
    Write-Host "  Duration: $([math]::Floor($metrics.Basic.Duration / 60))m $([math]::Floor($metrics.Basic.Duration % 60))s"
    Write-Host "  Bitrate: $($metrics.Basic.Bitrate) kbps"
    Write-Host "  Quality: $($metrics.AudioQualityScore)/100 ($($metrics.AudioQualityRating))" -ForegroundColor Green
}

# Generate HTML report
$htmlReport = @"
<!DOCTYPE html>
<html>
<head>
    <title>Audio Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #2c3e50; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .excellent { background-color: #d4edda; color: #155724; }
        .good { background-color: #d1ecf1; color: #0c5460; }
        .average { background-color: #fff3cd; color: #856404; }
        .poor { background-color: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>Audio Analysis Report</h1>
    <p>Generated on: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
    <p>Total files analyzed: $($results.Count)</p>
    
    <h2>File Details</h2>
    <table>
        <tr>
            <th>File</th>
            <th>Format</th>
            <th>Duration</th>
            <th>Sample Rate</th>
            <th>Bit Depth</th>
            <th>Channels</th>
            <th>Bitrate</th>
            <th>Quality</th>
        </tr>
"@

foreach ($result in $results) {
    $qualityClass = $result.Metrics.AudioQualityRating.ToLower()
    $htmlReport += @"
        <tr>
            <td>$($result.FileName)</td>
            <td>$($result.Metrics.Basic.Format.ToUpper())</td>
            <td>$([math]::Floor($result.Metrics.Basic.Duration / 60))m $([math]::Floor($result.Metrics.Basic.Duration % 60))s</td>
            <td>$($result.Metrics.Basic.SampleRate) Hz</td>
            <td>$($result.Metrics.Basic.BitDepth) bit</td>
            <td>$($result.Metrics.Basic.Channels)</td>
            <td>$($result.Metrics.Basic.Bitrate) kbps</td>
            <td class="$qualityClass">$($result.Metrics.AudioQualityScore)/100 ($($result.Metrics.AudioQualityRating))</td>
        </tr>
"@
}

$htmlReport += @"
    </table>
</body>
</html>
"@

# Save HTML report
$reportPath = "$outputDir\audio_analysis_report.html"
$htmlReport | Out-File -FilePath $reportPath -Encoding utf8

Write-Host "`n=== Analysis Complete ===" -ForegroundColor Green
Write-Host "Generated report: $((Resolve-Path $reportPath).Path)"

# Open the report in default browser
Start-Process $reportPath
