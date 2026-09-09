Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$wavPath = "sample_audio/test_speech.wav"
$synth.SetOutputToWaveFile($wavPath)
$synth.Speak("Hello, this is a verification call from the security department. Your account will be suspended within 10 minutes unless you verify your OTP code.")
$synth.Dispose()
Write-Host "Speech generated at $wavPath"
