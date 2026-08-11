<#
.SYNOPSIS
  Configure named VibeCast Gather and Cinematic AutoHideUI profiles offline.
.DESCRIPTION
  Refuses to write while WoW is running, preserves the original SavedVariables
  file beside it, validates an exact preimage on first apply, writes atomically,
  and never launches WoW or controls its UI.
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
  [string]$SavedVariablesPath = 'C:\Program Files (x86)\World of Warcraft\_retail_\WTF\Account\CERBERUS321\SavedVariables\AutoHideUI.lua',
  [string]$ExpectedSha256 = 'e9b75978022d496c99c4c2ce3fd1040a84e6983c07f8eb2af2e865688fc11d07',
  [string]$BackupPath = '',
  [string]$ReceiptPath = 'D:\WoW B-Roll Storage\_scripts\AUTOHIDEUI_CONFIG_LATEST.json',
  [switch]$AuditOnly,
  [switch]$SelfTest
)

$ErrorActionPreference = 'Stop'
$GatherProfile = 'VibeCast Gather'
$CinematicProfile = 'VibeCast Cinematic'
$GatherCustomFrames = 'ChatFrame1, ChatFrame2, ChatFrame3, ChatFrame4, ChatFrame5'

function Get-Sha256([string]$Path) {
  return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}

function Get-LuaTableSpan([string]$Text, [string]$Key, [int]$StartAt = 0) {
  $needle = '["' + $Key + '"] = {'
  $start = $Text.IndexOf($needle, $StartAt, [StringComparison]::Ordinal)
  if ($start -lt 0) { throw "Lua table not found: $Key" }
  $open = $Text.IndexOf('{', $start)
  $depth = 0
  $inString = $false
  $escaped = $false
  for ($i = $open; $i -lt $Text.Length; $i++) {
    $ch = $Text[$i]
    if ($inString) {
      if ($escaped) { $escaped = $false; continue }
      if ($ch -eq '\') { $escaped = $true; continue }
      if ($ch -eq '"') { $inString = $false }
      continue
    }
    if ($ch -eq '"') { $inString = $true; continue }
    if ($ch -eq '{') { $depth++ }
    elseif ($ch -eq '}') {
      $depth--
      if ($depth -eq 0) {
        return [pscustomobject]@{ Start = $start; Open = $open; End = $i; Length = ($i - $start + 1) }
      }
    }
  }
  throw "Unbalanced Lua table: $Key"
}

function Get-LuaBlock([string]$Text, [string]$Key) {
  $span = Get-LuaTableSpan -Text $Text -Key $Key
  return $Text.Substring($span.Start, $span.Length)
}

function Set-ProfileKeyValues([string]$Text) {
  $span = Get-LuaTableSpan -Text $Text -Key 'profileKeys'
  $block = $Text.Substring($span.Start, $span.Length)
  $updated = [regex]::Replace($block, '=\s*"Default"', '= "' + $GatherProfile + '"')
  if ($updated -eq $block) { throw 'No Default profileKeys were available to bind' }
  return $Text.Substring(0, $span.Start) + $updated + $Text.Substring($span.End + 1)
}

function Set-ProfileField([string]$Block, [string]$Name, [string]$Old, [string]$New) {
  $before = '["' + $Name + '"] = ' + $Old
  $after = '["' + $Name + '"] = ' + $New
  if (-not $Block.Contains($before)) { throw "Expected profile field absent: $before" }
  return $Block.Replace($before, $after)
}

function Set-AllListedFramesHidden([string]$ProfileBlock) {
  $span = Get-LuaTableSpan -Text $ProfileBlock -Key 'frames'
  $frames = $ProfileBlock.Substring($span.Start, $span.Length)
  $hidden = [regex]::Replace($frames, '(\["[^\"]+"\]\s*=\s*)false', '${1}true')
  return $ProfileBlock.Substring(0, $span.Start) + $hidden + $ProfileBlock.Substring($span.End + 1)
}

function Convert-ToVibeCastProfiles([string]$Text) {
  if ($Text.Contains('["' + $GatherProfile + '"] = {') -or $Text.Contains('["' + $CinematicProfile + '"] = {')) {
    throw 'One or more VibeCast profiles already exist; refusing a partial duplicate transform'
  }

  $working = Set-ProfileKeyValues -Text $Text
  $default = Get-LuaBlock -Text $working -Key 'Default'

  $gather = $default.Replace('["Default"] = {', '["' + $GatherProfile + '"] = {')
  $gather = Set-ProfileField -Block $gather -Name 'customFrames' -Old '""' -New ('"' + $GatherCustomFrames + '"')
  $gather = Set-ProfileField -Block $gather -Name 'ObjectiveTrackerFrame' -Old 'false' -New 'true'
  if (-not $gather.Contains('["MinimapCluster"] = false')) {
    throw 'Gather profile must preserve the minimap'
  }

  $cinematic = $default.Replace('["Default"] = {', '["' + $CinematicProfile + '"] = {')
  $cinematic = Set-ProfileField -Block $cinematic -Name 'customFrames' -Old '""' -New ('"' + $GatherCustomFrames + '"')
  $cinematic = Set-AllListedFramesHidden -ProfileBlock $cinematic

  $profiles = Get-LuaTableSpan -Text $working -Key 'profiles'
  $nl = if ($working.Contains("`r`n")) { "`r`n" } else { "`n" }
  $insert = $gather + ',' + $nl + $cinematic + ',' + $nl
  return $working.Substring(0, $profiles.End) + $insert + $working.Substring($profiles.End)
}

function Test-VibeCastProfiles([string]$Text) {
  $keys = Get-LuaBlock -Text $Text -Key 'profileKeys'
  $gather = Get-LuaBlock -Text $Text -Key $GatherProfile
  $cinematic = Get-LuaBlock -Text $Text -Key $CinematicProfile
  $cinematicFrames = Get-LuaBlock -Text $cinematic -Key 'frames'
  $checks = [ordered]@{
    profile_keys_bound_to_gather = ($keys.Contains('= "' + $GatherProfile + '"') -and -not $keys.Contains('= "Default"'))
    gather_custom_chat_hidden = $gather.Contains('["customFrames"] = "' + $GatherCustomFrames + '"')
    gather_objective_tracker_hidden = $gather.Contains('["ObjectiveTrackerFrame"] = true')
    gather_minimap_preserved = $gather.Contains('["MinimapCluster"] = false')
    cinematic_custom_chat_hidden = $cinematic.Contains('["customFrames"] = "' + $GatherCustomFrames + '"')
    cinematic_all_listed_frames_hidden = (-not [regex]::IsMatch($cinematicFrames, '\["[^\"]+"\]\s*=\s*false'))
  }
  $ok = -not ($checks.Values -contains $false)
  return [pscustomobject]@{ Ok = $ok; Checks = $checks }
}

function Write-AtomicUtf8([string]$Path, [string]$Body) {
  $parent = Split-Path -Parent $Path
  if (-not (Test-Path -LiteralPath $parent)) {
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
  }
  $tmp = Join-Path $parent ('.' + [IO.Path]::GetFileName($Path) + '.' + $PID + '.tmp')
  $utf8 = New-Object System.Text.UTF8Encoding($false)
  [IO.File]::WriteAllText($tmp, $Body, $utf8)
  Move-Item -LiteralPath $tmp -Destination $Path -Force
}

function New-Result([string]$State, [string]$PreSha, [string]$PostSha, [object]$Validation, [bool]$Mutated) {
  return [ordered]@{
    schema = 'gcs_autohideui_config/v1'
    generated_at_local = (Get-Date).ToString('o')
    status = if ($Validation.Ok) { 'PASS' } else { 'FAIL' }
    state = $State
    path = $SavedVariablesPath
    pre_sha256 = $PreSha
    post_sha256 = $PostSha
    backup_path = $BackupPath
    backup_sha256 = if ($BackupPath -and (Test-Path -LiteralPath $BackupPath)) { Get-Sha256 $BackupPath } else { $null }
    wow_running = [bool](Get-Process -Name 'Wow', 'WowClassic', 'WowClassicT' -ErrorAction SilentlyContinue)
    active_profile = $GatherProfile
    gather_profile = $GatherProfile
    cinematic_profile = $CinematicProfile
    checks = $Validation.Checks
    mutation = if ($Mutated) { 'offline_savedvariables_atomic_write' } else { 'none_read_only_or_idempotent' }
    original_preserved = [bool]($BackupPath -and (Test-Path -LiteralPath $BackupPath))
    may_publish = $false
    provider_effects = $false
  }
}

if ($SelfTest) {
  $fixture = @'
AutoHideUIDB = {
["profileKeys"] = {
["Fixture - Thrall"] = "Default",
},
["profiles"] = {
["Default"] = {
["groups"] = {
{
["config"] = {
["customFrames"] = "",
},
["frames"] = {
["ObjectiveTrackerFrame"] = false,
["MinimapCluster"] = false,
["PlayerFrame"] = true,
},
},
},
},
},
}
'@
  $converted = Convert-ToVibeCastProfiles -Text $fixture
  $test = Test-VibeCastProfiles -Text $converted
  if (-not $test.Ok) { throw 'AutoHideUI transform self-test failed' }
  [ordered]@{
    schema = 'gcs_autohideui_transform_selftest/v1'
    status = 'PASS'
    checks = $test.Checks
    mutation = 'fixture_only'
    may_publish = $false
  } | ConvertTo-Json -Depth 6
  exit 0
}

if (-not (Test-Path -LiteralPath $SavedVariablesPath)) {
  throw "SavedVariables file missing: $SavedVariablesPath"
}
if (-not $BackupPath) { $BackupPath = $SavedVariablesPath + '.pre-vibecast-20260811.bak' }

$current = Get-Content -LiteralPath $SavedVariablesPath -Raw
$preSha = Get-Sha256 $SavedVariablesPath
$already = $current.Contains('["' + $GatherProfile + '"] = {') -and $current.Contains('["' + $CinematicProfile + '"] = {')

if ($already) {
  $validation = Test-VibeCastProfiles -Text $current
  $result = New-Result -State 'ALREADY_CONFIGURED' -PreSha $preSha -PostSha $preSha -Validation $validation -Mutated $false
  if (-not $AuditOnly -and $ReceiptPath) { Write-AtomicUtf8 -Path $ReceiptPath -Body (($result | ConvertTo-Json -Depth 7) + "`n") }
  $result | ConvertTo-Json -Depth 7
  exit $(if ($validation.Ok) { 0 } else { 2 })
}

$unconfigured = [pscustomobject]@{ Ok = $false; Checks = [ordered]@{ profiles_configured = $false } }
if ($AuditOnly) {
  (New-Result -State 'NEEDS_CONFIGURATION' -PreSha $preSha -PostSha $preSha -Validation $unconfigured -Mutated $false) | ConvertTo-Json -Depth 7
  exit 1
}

if ([bool](Get-Process -Name 'Wow', 'WowClassic', 'WowClassicT' -ErrorAction SilentlyContinue)) {
  throw 'WoW is running; offline SavedVariables configuration refused'
}
if ($ExpectedSha256 -and $preSha -ne $ExpectedSha256.ToLowerInvariant()) {
  throw "Unexpected AutoHideUI preimage: $preSha"
}
if (Test-Path -LiteralPath $BackupPath) {
  if ((Get-Sha256 $BackupPath) -ne $preSha) { throw "Existing backup does not match the admitted original: $BackupPath" }
} else {
  Copy-Item -LiteralPath $SavedVariablesPath -Destination $BackupPath
}

$converted = Convert-ToVibeCastProfiles -Text $current
$preview = Test-VibeCastProfiles -Text $converted
if (-not $preview.Ok) { throw 'Converted profile validation failed before write' }

if (-not $PSCmdlet.ShouldProcess($SavedVariablesPath, 'write VibeCast AutoHideUI profiles')) {
  (New-Result -State 'WHATIF_VALID' -PreSha $preSha -PostSha $preSha -Validation $preview -Mutated $false) | ConvertTo-Json -Depth 7
  exit 0
}

Write-AtomicUtf8 -Path $SavedVariablesPath -Body $converted
$readback = Get-Content -LiteralPath $SavedVariablesPath -Raw
$validation = Test-VibeCastProfiles -Text $readback
$postSha = Get-Sha256 $SavedVariablesPath
$result = New-Result -State 'CONFIGURED' -PreSha $preSha -PostSha $postSha -Validation $validation -Mutated $true
if ($ReceiptPath) { Write-AtomicUtf8 -Path $ReceiptPath -Body (($result | ConvertTo-Json -Depth 7) + "`n") }
$result | ConvertTo-Json -Depth 7
exit $(if ($validation.Ok) { 0 } else { 2 })
