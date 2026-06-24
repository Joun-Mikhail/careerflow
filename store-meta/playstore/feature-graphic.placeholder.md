# Play Store feature graphic

Required: **1024×500 PNG or JPEG**, no transparency, no text on the edges.

Drop the real artwork in this directory as `feature-graphic.png` and remove
this placeholder before submitting. The Fastlane `supply` lane in
[`fastlane/android/Fastfile`](../../fastlane/android/Fastfile) uploads
everything under `fastlane/metadata/android/en-US/images/`; symlink or copy
the final graphic into that location at submission time.
