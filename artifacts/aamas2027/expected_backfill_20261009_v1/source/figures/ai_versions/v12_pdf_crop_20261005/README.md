# v12 — superseded crop-only publication candidate

v11 is scientifically complete but its raster canvas contains large white top
and bottom margins. At full text width this adds enough vertical height to push a
single bibliography entry onto an eighth page. v12 keeps the v11 pixels and
removes only the empty canvas margin for PDF placement. v11 remains the source
candidate and is not overwritten.

Files:

- `candidate_uncropped.png`: v11 raster candidate, retained unchanged;
- `candidate_cropped.png`: crop-only PDF placement candidate;
- cropped SHA-256: `64a39b1f064ede8de502c3174aade0e2392d07b2a5528b6150c6dad6b4fbdb26`.

Temporary AAMAS layout validation passed with 7 pages, zero overfull boxes, and
no unresolved references. The independent audit then found no P0 semantic
defects and two low-risk P1 presentation notes (the explore relation can be
made more explicit in the caption, and small labels should be checked at final
print scale). The candidate was previously promoted to active, then superseded
by the icon-first v14 figure. It remains available at `overview_v12.pdf`; its
SHA-256 is
`666940c307a94a1694a3bfd585a72fead69e23923d3ab9ef9b466985fa59dca9`.
