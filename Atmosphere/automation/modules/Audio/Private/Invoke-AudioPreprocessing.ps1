function Invoke-AudioPreprocessing {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$InputFile,
        
        [string]$OutputFile,
        
        [int]$SampleRate = 44100,
        
        [int]$Channels = 2,
        
        [ValidateSet('wav', 'flac', 'mp3')]
        [string]$Format = 'wav',
        
        [switch]$Normalize,
        
        [switch]$RemoveSilence
    )
    
    try {
        # Ensure the module is initialized
        if (-not $script:ModuleInitialized) {
            Initialize-AudioModule
        }
        
        Write-Log -Message "Starting audio preprocessing for: $InputFile" -Level Debug -Source 'AudioPreprocessing'
        
        # Validate input file
        if (-not (Test-Path -Path $InputFile)) {
            throw "Input file not found: $InputFile"
        }
        
        # Set default output file if not specified
        if ([string]::IsNullOrEmpty($OutputFile)) {
            $OutputFile = [System.IO.Path]::ChangeExtension($InputFile, $Format)
        }
        
        # Create output directory if it doesn't exist
        $outputDir = [System.IO.Path]::GetDirectoryName($OutputFile)
        if (-not [string]::IsNullOrEmpty($outputDir) -and -not (Test-Path -Path $outputDir)) {
            New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
        }
        
        # Build FFmpeg command
        $ffmpegArgs = @(
            '-i', "`"$InputFile`"",
            '-ar', $SampleRate,
            '-ac', $Channels,
            '-y'  # Overwrite output file if it exists
        )
        
        # Add format-specific options
        switch ($Format) {
            'wav' { $ffmpegArgs += @('-f', 'wav', '-c:a', 'pcm_s16le') }
            'flac' { $ffmpegArgs += @('-f', 'flac', '-compression_level', '8') }
            'mp3' { $ffmpegArgs += @('-f', 'mp3', '-q:a', '0') }
        }
        
        # Add effects
        $filterComplex = @()
        
        if ($Normalize) {
            $filterComplex += 'loudnorm=I=-16:TP=-1.5:LRA=11'
        }
        
        if ($RemoveSilence) {
            $filterComplex += 'silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.1:start_duration=0.1'
        }
        
        if ($filterComplex.Count -gt 0) {
            $ffmpegArgs += '-af', ($filterComplex -join ',')
        }
        
        # Add output file
        $ffmpegArgs += "`"$OutputFile`""
        
        # Run FFmpeg
        $process = Start-Process -FilePath 'ffmpeg' -ArgumentList $ffmpegArgs -NoNewWindow -Wait -PassThru -RedirectStandardError 'nul'
        
        if ($process.ExitCode -ne 0) {
            throw "FFmpeg processing failed with exit code $($process.ExitCode)"
        }
        
        if (-not (Test-Path -Path $OutputFile)) {
            throw "Output file was not created: $OutputFile"
        }
        
        Write-Log -Message "Successfully processed audio file: $OutputFile" -Level Debug -Source 'AudioPreprocessing'
        
        return [PSCustomObject]@{
            InputFile = $InputFile
            OutputFile = $OutputFile
            Format = $Format
            SampleRate = $SampleRate
            Channels = $Channels
            FileSize = (Get-Item -Path $OutputFile).Length
            ProcessingTime = $process.ExitTime - $process.StartTime
        }
    }
    catch {
        Write-Log -Message "Audio preprocessing failed: $_" -Level Error -Source 'AudioPreprocessing'
        throw $_
    }
}
