# Resume WoW capture today

The Mac and Windows scripts are already synchronized. You do not need to send
an agent a proceed message or manually move files.

## Required: about one minute before play

1. Open OBS and choose **WoW B-Roll 1440p60** (WoW_BRoll_1440p60), not Fable.
2. Confirm the preview shows WoW and both **Desktop Audio** and **Mic** meters move.
3. Record ten seconds while game sound is playing and say one sentence.
4. Stop and play that test back. Continue only if game and voice are both audible.

## Then play

1. Press **Record**.
2. Auto Hide UI is preconfigured: **VibeCast Gather** is active and keeps the
   minimap while hiding chat and the objective tracker. For a clean orbit, use
   `/autohide setProfile VibeCast Cinematic`; switch back with
   `/autohide setProfile VibeCast Gather`.
3. If the Stream Deck capture page is ready, press record_start once. Other
   markers such as talk_peak, funny_moment, and skip_zone are optional.
4. Play normally. For one clean orbit, use the Cinematic profile or **Alt+Z**
   for about 15 seconds.
5. Press **Stop** when the fun ends.
6. After the file has stopped growing, run:

    powershell -NoProfile -ExecutionPolicy Bypass -File "D:\WoW B-Roll Storage\_scripts\Session-End-Ship.ps1"

Then walk away. The Mac watchers own polling, transfer, harvest, scoring, and
the review-pack update. Packages remain **NOT_ARMED**.

## Optional: do not delay the play session

- The original Auto Hide UI SavedVariables file is backed up beside the live
  file as `AutoHideUI.lua.pre-vibecast-20260811.bak`.
- If the named profiles do not appear after login, Alt+Z is enough for today's
  clean-orbit proof; do not delay play to troubleshoot UI.
- Later, spend one minute choosing the best League clips and framing **A or B**
  in the local review board.

## Stop conditions

- Do not use the Fable OBS profile.
- Do not continue if either audio meter is dead.
- Do not arm or publish anything from Windows.
