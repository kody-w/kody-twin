#!/bin/bash
#
# Mirror installer — thin proxy to the grail kernel installer.
#
# Per the Mirror Spec (https://kody-w.github.io/RAPP/pages/vault/), every
# valid mirror's installer re-fetches the canonical installer from the
# grail's raw GitHub URL on every run, so no mirror's installer can drift
# from the upstream source of truth.

set -e

GRAIL_INSTALLER_URL="https://raw.githubusercontent.com/kody-w/rapp-installer/main/install.sh"

curl -fsSL "$GRAIL_INSTALLER_URL" | bash -s -- "$@"
