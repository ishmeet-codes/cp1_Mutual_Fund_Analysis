param(
    [Parameter(Mandatory=$true)]
    [string]$PptxPath,
    [Parameter(Mandatory=$true)]
    [string]$OutDir
)

if (-not (Test-Path $PptxPath)) {
    Write-Error "PPTX not found: $PptxPath"
    exit 1
}

if (-not (Test-Path $OutDir)) {
    New-Item -ItemType Directory -Path $OutDir | Out-Null
}

# Requires Microsoft Office/PowerPoint installed on the machine
$pp = New-Object -ComObject PowerPoint.Application
try {
    $pp.Visible = $true
    $pres = $pp.Presentations.Open($PptxPath, $false, $false, $false)
    # 18 = ppSaveAsPNG
    $pres.SaveAs((Resolve-Path $OutDir).ProviderPath, 18)
    $pres.Close()
} finally {
    $pp.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($pp) | Out-Null
}

Write-Output "Export complete. PNG folders are under: $OutDir"
