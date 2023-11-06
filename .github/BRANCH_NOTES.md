This branch contains the first revision for ARM64 snap releases. It contains
- Update mongo to 4.4 (migrations/00-adopt-version)
- epoch 5*
- Disabled 00-new_snap_initializations.sh and 01-check_avx.sh (could be removed earlier, but doesn't hurt)
- Disabled 00-adopt-version migration as not required anymore (mongo update stops here)