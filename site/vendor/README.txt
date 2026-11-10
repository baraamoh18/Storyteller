The reader's animation library and fonts, served with the reader itself so that it asks no other server for anything
(quicker on a phone, and the PC reader works without the internet).

gsap.min.js, ScrollTrigger.min.js   GSAP 3.12.5 (npm: gsap@3.12.5, dist/). Copyright GreenSock. Free to use under
                                    GSAP's standard "no charge" licence: https://gsap.com/standard-license
qrcode.js                           qrcode-generator 1.4.4 (npm: qrcode-generator@1.4.4). MIT licence,
                                    (c) 2009 Kazuhiko Arase. Only loaded by the PC reader ("Read on your phone").
fonts/bangers-latin-400-normal.woff2            Bangers            (npm: @fontsource/bangers@5.1.0)
fonts/archivo-narrow-latin-400/600-normal.woff2 Archivo Narrow     (npm: @fontsource/archivo-narrow@5.1.0)
fonts/ibm-plex-mono-latin-500-normal.woff2      IBM Plex Mono      (npm: @fontsource/ibm-plex-mono@5.1.0)
                                    All three fonts: SIL Open Font Licence 1.1, https://openfontlicense.org
                                    (Latin subset, the same files Google Fonts serves).

To update GSAP: replace the two files with the same names from the new version's dist/ folder, then run the reader's
checks (site/README.md, "Performance"). index.html falls back to cdnjs 3.12.5 only when these files are missing.
