# Asset and license provenance inventory

Primary-source review and local metadata inspection: **20 September 2026**. This inventory records evidence and remaining gaps; it grants no new rights. Public attribution for this project is **christopher robin fiore**, under **globalanomalyindex/wildcard**.

## Bundled fonts

### Karrik Regular: upstream license and exact file match verified

[Karrik's official Velvetyne page](https://velvetyne.fr/fonts/karrik/) identifies Jean-Baptiste Morizot and Lucas Le Bihan as its designers and lists the SIL Open Font License, version 1.1. Its [official download page](https://velvetyne.fr/download/?font=karrik) links to the authors' [Karrik Fonts source repository](https://gitlab.com/phantomfoundry/karrik_fonts). The publisher permits personal and commercial use, including websites, and requests credit to the designers and Velvetyne.

The downloaded official archive contained `fonts/Desktop/OTF/Karrik-Regular.otf`, which matched this repository's `site/fonts/Karrik-Regular.otf` **byte for byte**. The accompanying [upstream LICENCE.txt](https://gitlab.com/phantomfoundry/karrik_fonts/-/blob/main/LICENCE.txt) declares OFL 1.1. This connects the actual bundled binary to a published license rather than inferring permission from the family name.

| Evidence | Value |
|---|---|
| Local and upstream font SHA-256 | `3913880b1ff60f9efb6d22cc790ac2fc938ed6550ccd92727bf910da8ab1b405` |
| Local font size | 79,808 bytes |
| Embedded version | `Version 1.500` |
| Embedded unique name | `Karrik-Regular:Jean-BaptisteMorizot;LucasLeBihan:1.5` |
| Official archive URL checked | [karrik_fonts-main.zip](https://gitlab.com/phantomfoundry/karrik_fonts/-/archive/main/karrik_fonts-main.zip) |
| Archive SHA-256 at inspection | `0272d94e93e56d94a1119235ab1c05e6adf5eb65e9c04d25e8451fdf5dc00ac9` |

The bundled font has no name-table copyright record or license description/URL records (IDs 0, 13, or 14). Its `OS/2.fsType` value is 4. Neither that metadata nor this summary substitutes for the upstream license. The formerly missing [upstream license text](site/fonts/Karrik-OFL.txt) is now bundled without alteration, together with [designer credits and source provenance](site/fonts/Karrik-CREDITS.md). The 4,384-byte license file has SHA-256 `549e89d0f852d867c6c753e5f39251e66135d22e81563a907ee7ac3c23d2f4a8`. Under the [official OFL terms](https://openfontlicense.org/open-font-license-official-text/), redistribution and bundling are permitted subject to conditions, including preservation of the relevant notice and license, licensing the font under OFL, and respecting any Reserved Font Names when modifying it. This packaging step does not modify the font.

Credit: **Karrik by Jean-Baptiste Morizot and Lucas Le Bihan, distributed by Velvetyne, under SIL OFL 1.1.**

### Rubik Bubbles Regular: current display font, OFL bundled

The current display role uses `site/fonts/RubikBubbles-Regular.ttf`, obtained from the [Google Fonts source repository](https://github.com/google/fonts/tree/main/ofl/rubikbubbles). Its [upstream OFL notice](https://github.com/google/fonts/blob/main/ofl/rubikbubbles/OFL.txt) is bundled as [RubikBubbles-OFL.txt](site/fonts/RubikBubbles-OFL.txt), including the copyright notice for **The Rubik Filtered Project Authors, 2020**. The original notice is preserved, including its upstream URL spelling. The font is under SIL OFL 1.1; this does not relicense it as project code.

| Evidence | Value |
|---|---|
| Font source | [RubikBubbles-Regular.ttf](https://raw.githubusercontent.com/google/fonts/main/ofl/rubikbubbles/RubikBubbles-Regular.ttf) |
| Font SHA-256 | `2171521dab2b1b3675bbb7aecd34b1c169167c360e3647dadb4939910490c974` |
| Font size | 219,564 bytes |
| Bundled upstream license SHA-256 | `f9e2d4498ea80d38bac7b8841d68af68c132fa67e1552e7c05717e6987de1d74` |
| License file size | 4,406 bytes |
| Acquisition date | 20 September 2026 |

Rubik Bubbles was selected for the rounded display role as a licensed alternative to the previously bundled Boyers Blur. Karrik remains the body face. No commercial font purchase was made for this replacement.

### Historical Boyers Blur: maker identified, entitlement unresolved

`site/fonts/BoyersBlur-Regular.otf` was removed from the current tree on 20 September 2026; its prior presence remains in Git history. The inspected historical binary contains the copyright record “Copyright © 2023 by Craft Supply Co. All rights reserved.” It identifies Craft Supply Co as manufacturer/designer and links to the foundry. The embedded version is `1.000`. It contains no license description or license URL in name IDs 13 or 14. Its SHA-256 is `99be0a714a54431daf750c1fde491551304ef255b13a91173c1e32895ca436fd` and its size is 30,804 bytes.

The foundry's [Boyers Blur product page](https://craftsupply.co/product/boyers-blur-font/) offers different licenses. Its [official license page](https://craftsupply.co/licenses/) describes Website use separately from Desktop use, including WOFF delivery, one website, and a 100,000 monthly page-view allowance for the listed Website option. Other listed options differ. These public descriptions establish available license categories; they do not identify which license, if any, the project owner obtained or the terms of that acquisition.

The historical [implementation plan](docs/superpowers/plans/2026-06-10-wildcard-landing.md) records copying both fonts from the local font library. A local installation is not a purchase receipt or evidence of permission to distribute the binary through a public source repository. No project-specific receipt, applicable EULA, or redistribution authorization was found in the repository. This is **unresolved entitlement evidence**, not a finding that the owner has no license.

The inspected historical Karrik and Boyers Blur binaries both have `OS/2.fsType = 4`. The [OpenType specification](https://learn.microsoft.com/en-us/typography/opentype/spec/os2#fstype) defines this as preview-and-print embedding, with read-only document behavior. It is not a general open-source or unrestricted web-redistribution grant. It should not be edited to manufacture permission. Karrik's published OFL and exact upstream match provide separate license evidence, as documented above.

The deployed font choice now avoids relying on this unresolved entitlement. Removal from the current tree does not establish whether earlier uses or redistribution were covered by a license.

## Raster assets

The current tree contains three raster assets and two active font binaries, Karrik and Rubik Bubbles, plus their text notices. No additional standalone image, video, audio, or font files were identified outside generated research records or dependency directories.

| Asset | Local evidence | SHA-256 |
|---|---|---|
| `docs/design-assets/chickpea-grid.png` | 1067 × 1600 pixels; no text or EXIF metadata. | `ffe1812c60efda33c6372bbb1d62a6276301192e6461c3bb5a5551682603253e` |
| `site/assets/chickpea-grid-display.png` | 1600 × 1067 pixels; EXIF stores color space and dimensions, with no author or license field. | `662ecb4c5fe558dc1aa51284a447f1b5798240fc27abf40625c37af124f04418` |
| `docs/design-assets/figma-desktop-1.png` | 1440 × 1024 pixels; its text metadata says `Software=Figma`, with no author or license. | `87e07950a98768769189277750d546d68a0843e9a59ed713577a8d179d07166d` |

The [historical design specification](docs/superpowers/specs/2026-06-10-wildcard-landing-design.md) describes the Chickpea image as a user-supplied reference and records deriving layout measurements and the rotated display asset from it. It also describes the Figma source frame. Those notes do not identify the original image creator, a source publication URL, or applicable reuse terms. A bounded public search did not recover a reliable primary source for these specific images. Their rights chain remains unresolved; a filename, image dimensions, or an export-tool label is not evidence of a license.

If the image provenance cannot be recovered, an independently authored grid illustration with recorded source geometry can serve the decorative role in the deployed page. Such a replacement should not be presented as a licensed copy of the original image. Historical reference files and any public redistribution of them require their own provenance decision; changing the deployed page does not erase that distinction.

## Code and corpus declarations

| Material | Verified repository evidence | Remaining limitation |
|---|---|---|
| Plugin code and instructions | `plugin/.claude-plugin/plugin.json` declares `MIT`. | No root LICENSE text was present in the audited checkout. This review does not invent copyright ownership or supply a new project license. |
| Concept-title snapshot | Headers and [concept sourcing notes](docs/concepts-sourcing.md) identify Wikipedia Vital Articles L3/L4, retrieval date 2026-06-12, and CC BY-SA attribution for source text. The runtime uses title labels rather than article prose. | Individual source revisions and complete editorial decisions were not recorded. This observation does not establish that every title, asset, or downstream reuse is exempt from rights obligations. |

The project byline and AI assistance do not resolve third-party rights. The source facts above support a concrete packaging decision for Karrik and identify the evidence still needed for Boyers Blur and the reference images.
