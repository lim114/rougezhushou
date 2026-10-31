# Game recognition template assets

`rouge/data/ui-icons/potential-1.png` through `potential-6.png` are game UI assets obtained from
[Aceship/Arknight-Images](https://github.com/Aceship/Arknight-Images/tree/main/ui/potential).
They are used as local recognition templates. Original game asset rights remain with their respective owners;
this project does not relicense the artwork under its code license.

Exact source URLs, Git blob identities and SHA-256 values are recorded in
`rouge/data/ui-icon-receipt.json`. The downloader verifies the listed Git blob identity.

Elite phase templates (`elite-0.png` through `elite-2.png` and their `-s` variants)
also come from Aceship/Arknight-Images, commit
`0b28f9562fcadbd644c6225f8f8aefbb500b4d22`, under `ui/elite/`.
Source URLs, Git blobs and SHA-256 hashes are recorded in `rouge/data/elite-icon-receipt.json`.

233 collectible templates under `rouge/data/relic-icons/` come from
[fexli/ArknightsResource](https://github.com/fexli/ArknightsResource), commit
`d0b5af0b004b044d322397ce5ae79632b6d9fcdd`, under `rogueitem/`.
`rouge/data/relic-icon-receipt.json` records successful and unavailable references,
source URLs, Git blobs and SHA-256 hashes. Downloaders verify the Git blob identity
before saving files; missing references are not fabricated.

The upstream [legal notice](https://github.com/fexli/ArknightsResource#0x00-legal-notice)
attributes game files to Hypergryph and describes educational and research use.
These templates are used for local visual recognition. Game artwork remains the
property of its rights holders and is not relicensed under this project's code license.

`emergency-marker.png` (person/clock) and `advanced-marker.png` (progression diamond)
are separate recognition crops from an authorized local game-window
capture (`samples/native-client/run-emergency-mechanist.png`). Crop coordinates
and source/image hashes are recorded in `rouge/data/emergency-icon-receipt.json`.
It remains game artwork owned by its rights holders, not original project artwork.

Additional display-only collectible/legacy pictures are recorded in
`rouge/data/relic-display-icons.json`, from fexli/ArknightsResource commit
`184aa662f210100150716d4f58cadc0b4e3642fc`, under `rogueitem/`.
The 21 verified original references use 16 unique PNGs under
`rouge/data/relic-display-icons/`; only exact whole-byte duplicates share a file.
All stored PNGs retain exact upstream bytes. Four additional records are explicitly labelled group-picture references
from pinned game `itemIconGroupId` declarations, not verified independent variant
art. They do not extend recognition templates or prove possession/effect state.
The upstream Hypergryph copyright/educational-use notice applies; these images
are not relicensed under this project's code license.
