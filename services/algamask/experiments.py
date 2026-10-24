"""Versioned engineering assumptions from FIRST_RELEASE_SCOPE.md; not approval."""

PROOF_VERSION = "spirulina-proof-v1"


def proof_amounts(code):
    # Return a fresh mapping. Never scale, optimize or silently substitute forms.
    arms = {
        "B0": {"IF-OAT-DRY": 30.60, "IF-DATE-DRIED": 13.50, "IF-COCOA-PWD": 0.90},
        "A0": {"IF-OAT-DRY": 29.70, "IF-DATE-DRIED": 13.50, "IF-COCOA-PWD": 0.90,
               "IF-SPI-PWD": 0.90},
        "A1": {"IF-OAT-DRY": 29.25, "IF-DATE-DRIED": 13.50, "IF-COCOA-PWD": 0.90,
               "IF-SPI-PWD": 0.90, "IF-CINN-PWD": 0.45},
    }
    return arms.get(code)
