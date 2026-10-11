# Generates listening exercises using the installed English Windows voice.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$defenseItems = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'questions.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$defenseSynth = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $defenseSynth.SelectVoice('Microsoft Zira Desktop')
    $defenseModes = @(
        @{ Name = 'questions_slow.wav'; Rate = -2; Pause = 4; Answers = $false },
        @{ Name = 'questions_normal.wav'; Rate = 0; Pause = 2; Answers = $false },
        @{ Name = 'answers_normal.wav'; Rate = 0; Pause = 3; Answers = $true }
    )
    foreach ($defenseMode in $defenseModes) {
        $defensePrompt = New-Object System.Speech.Synthesis.PromptBuilder ([System.Globalization.CultureInfo]::GetCultureInfo('en-US'))
        $defensePrompt.AppendText('English thesis defense practice. Synthetic voice. Pause the recording after each question and try your own answer.')
        $defensePrompt.AppendBreak([TimeSpan]::FromSeconds(2))
        foreach ($defenseItem in $defenseItems) {
            $defensePrompt.AppendText("Question $($defenseItem.id).")
            $defensePrompt.AppendBreak([TimeSpan]::FromMilliseconds(400))
            $defensePrompt.AppendText($defenseItem.question)
            $defensePrompt.AppendBreak([TimeSpan]::FromSeconds($defenseMode.Pause))
            if ($defenseMode.Answers) {
                $defensePrompt.AppendText('Example answer.')
                $defensePrompt.AppendText($defenseItem.answer)
                $defensePrompt.AppendBreak([TimeSpan]::FromSeconds(3))
            }
        }
        $defenseSynth.Rate = $defenseMode.Rate
        $defenseOutput = Join-Path $PSScriptRoot $defenseMode.Name
        $defenseSynth.SetOutputToWaveFile($defenseOutput)
        $defenseSynth.Speak($defensePrompt)
        $defenseSynth.SetOutputToNull()
        Get-Item -LiteralPath $defenseOutput | Select-Object Name,Length
    }
} finally {
    $defenseSynth.Dispose()
}
