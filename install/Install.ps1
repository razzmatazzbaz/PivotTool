$code = Get-Content -Raw -Path "install/Install.cs"
Add-Type -TypeDefinition "$code"

[Install]::Main()