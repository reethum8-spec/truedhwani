Add-Type -AssemblyName System.Speech

$samples = @(
    @{
        File = "sample_audio/otp_scam_call.wav"
        Text = "Sir I am calling from State Bank verification unit. Your debit card has been blocked due to suspicious activity. I have sent a 6-digit OTP code to your registered mobile number. Please share the OTP code immediately to unblock your account."
    },
    @{
        File = "sample_audio/benign_call.wav"
        Text = "Hi Rahul, hope you are doing well today. I was reviewing the notes from our team meeting and wanted to check if you have time for a quick project sync after lunch tomorrow."
    },
    @{
        File = "sample_audio/kyc_scam_call.wav"
        Text = "This is customs department Mumbai airport. A parcel containing illegal items and passports registered under your Aadhaar number has been seized. An arrest warrant will be issued if you do not complete biometric KYC immediately."
    }
)

foreach ($item in $samples) {
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synth.SetOutputToWaveFile($item.File)
    $synth.Speak($item.Text)
    $synth.Dispose()
    Write-Host "Generated: $($item.File)"
}
