──────────────────────────────── Overall Stats ─────────────────────────────────
Num Passed Tests : 5
Num Failed Tests : 1
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
>> Passed Requirement
assert all added downloaded song_ids are in private_data.library_song_ids
>> Passed Requirement
assert all added downloaded song_ids are in private_data.liked_song_ids
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
[2, 11, 14, 27, 48, 94]
==
[2, 11, 14, 27, 48, 94, 119, 131, 147, 173, 182, 190, 192, 197, 229, 233, 235,
251, 289, 303, 324]

In right but not left:
[119, 131, 147, 173, 182, 190, 192, 197, 229, 233, 235, 251, 289, 303, 324]

Original values:
[27, 48, 94, 11, 2, 14]
==
[192, 2, 131, 324, 197, 11, 14, 147, 27, 94, 289, 229, 233, 235, 173, 303, 48,
182, 119, 251, 190]