──────────────────────────────── Overall Stats ─────────────────────────────────
Num Passed Tests : 3
Num Failed Tests : 3
Num Total  Tests : 6
──────────────────────────────────── Passes ────────────────────────────────────
>> Passed Requirement
assert answers match.
>> Passed Requirement
assert model changes match spotify.UserDownloadedSong.
>> Passed Requirement
obtain added, updated, removed spotify.UserDownloadedSong records using
models.changed_records,
and assert 0 have been removed.
──────────────────────────────────── Fails ─────────────────────────────────────
>> Failed Requirement
assert added downloaded song_ids match private_data.to_download_song_ids
(ignore_order=True)
```python
with test(
    """
    assert added downloaded song_ids match private_data.to_download_song_ids
(ignore_order=True)
    """
):
    downloaded_song_ids = list_of(added_downloaded_songs, "song_id")
    test.case(downloaded_song_ids, "==", private_data.to_download_song_ids,
ignore_order=True)
```
----------
AssertionError:
[2, 11, 13, 14, 35, 36, 48, 55, 67, 76, 79, 83, 97, 98, 101, 114, 119, 155, 159,
161, 163, 165, 175, 197, 211, 218, 221, 229, 233, 234, 240, 245, 251, 270, 272,
292, 294, 301, 304, 307, 313, 319, 321]
==
[2, 11, 14, 27, 48, 94, 119, 131, 147, 173, 182, 190, 192, 197, 229, 233, 235,
251, 289, 303, 324]

In left but not right:
[13, 35, 36, 55, 67, 76, 79, 83, 97, 98, 101, 114, 155, 159, 161, 163, 165, 175,
211, 218, 221, 234, 240, 245, 270, 272, 292, 294, 301, 304, 307, 313, 319, 321]

In right but not left:
[27, 94, 131, 147, 173, 182, 190, 192, 235, 289, 303, 324]

Original values:
[14, 165, 272, 229, 97, 197, 98, 234, 233, 292, 155, 307, 245, 218, 2, 321, 251,
161, 270, 76, 211, 313, 36, 67, 35, 13, 101, 114, 48, 294, 301, 175, 79, 159,
240, 163, 55, 11, 119, 221, 304, 83, 319]
==
[192, 2, 131, 324, 197, 11, 14, 147, 27, 94, 289, 229, 233, 235, 173, 303, 48,
182, 119, 251, 190]
>> Failed Requirement
assert all added downloaded song_ids are in private_data.library_song_ids
```python
with test(
    """
    assert all added downloaded song_ids are in private_data.library_song_ids
    """
):
    test.case(downloaded_song_ids, "all in", private_data.library_song_ids)
```
----------
AssertionError:
272
in
[2, 131, 11, 14, 147, 277, 27, 289, 290, 163, 292, 165, 294, 44, 173, 303, 175,
48, 307, 54, 182, 313, 61, 190, 319, 192, 324, 197, 76, 77, 211, 94, 99, 229,
233, 106, 235, 236, 234, 119, 121, 251]
>> Failed Requirement
assert all added downloaded song_ids are in private_data.liked_song_ids
```python
with test(
    """
    assert all added downloaded song_ids are in private_data.liked_song_ids
    """
):
```
----------
AssertionError:
165
in
[2, 131, 135, 11, 14, 15, 142, 147, 21, 27, 30, 31, 289, 34, 35, 297, 173, 303,
48, 182, 190, 192, 320, 324, 197, 80, 81, 82, 94, 99, 100, 229, 233, 235, 117,
119, 251]