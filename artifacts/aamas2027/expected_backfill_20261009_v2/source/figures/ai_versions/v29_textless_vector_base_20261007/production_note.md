# v29 production-path note

AI image generation supplies the complete visual base and glyph composition. The v29 base deliberately
contains no words, so the visible labels can be typeset with an embedded TrueType font in a separate PDF
wrapper. This is a production conversion, not a replacement of the AI visual design.

The wrapper is intentionally kept in this version directory and is not connected to the active paper until
`pdffonts`, paper-scale rendering, grayscale inspection, and semantic comparison all pass.
