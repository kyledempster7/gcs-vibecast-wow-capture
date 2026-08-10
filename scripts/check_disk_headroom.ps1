# Quick disk headroom before long record (Windows)
$targets = @("D:\", "C:\")
foreach ($t in $targets) {
  $d = Get-PSDrive -Name $t.TrimEnd(":\").Substring(0,1) -ErrorAction SilentlyContinue
  if (-not $d) { try { $drive = (Get-Volume -DriveLetter $t[0] -ErrorAction SilentlyContinue) } catch {} }
}
Get-Volume | Where-Object { $_.DriveLetter -in @('C','D') } | ForEach-Object {
  $freeGB = [math]::Round($_.SizeRemaining/1GB, 1)
  $totalGB = [math]::Round($_.Size/1GB, 1)
  $pct = if ($_.Size -gt 0) { [math]::Round(100*$_.SizeRemaining/$_.Size, 1) } else { 0 }
  $flag = if ($freeGB -lt 30) { "LOW" } else { "OK" }
  "{0}: {1} free / {2} total GB ({3}%) [{4}]" -f $_.DriveLetter, $freeGB, $totalGB, $pct, $flag
}
