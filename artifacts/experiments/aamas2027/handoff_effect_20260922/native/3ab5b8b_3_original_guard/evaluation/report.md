──────────────────────────────── Overall Stats ─────────────────────────────────
Num Passed Tests : 4
Num Failed Tests : 2
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
AssertionError:  [47, 48, 49, 50, 51, 52, 53] == [31, 32, 48, 49, 50, 51, 52,
57]

In left but not right:
[47, 53]

In right but not left:
[31, 32, 57]

Original values:
[47, 52, 50, 48, 49, 51, 53] == [32, 48, 49, 50, 51, 52, 57, 31]
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
47
in
[262, 135, 138, 270, 144, 273, 148, 21, 156, 286, 31, 32, 164, 293, 294, 169,
48, 49, 50, 51, 52, 176, 177, 55, 57, 58, 59, 64, 194, 195, 196, 77, 206, 82,
90, 91, 92, 102, 107, 112, 116]