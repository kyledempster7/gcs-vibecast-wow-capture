# Verify Memento addon folder exists (post-patch check)
$path = "C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns\Memento"
$shots = "C:\Program Files (x86)\World of Warcraft\_retail_\Screenshots"
if (Test-Path $path) { "MEMENTO_ADDON=OK $path" } else { "MEMENTO_ADDON=MISSING $path" }
if (Test-Path $shots) {
  $n = (Get-ChildItem $shots -File -ErrorAction SilentlyContinue | Measure-Object).Count
  "SCREENSHOTS=OK count=$n"
} else { "SCREENSHOTS=MISSING" }
