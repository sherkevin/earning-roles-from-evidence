"""Synthetic code-generation invariants; never used as task evidence."""
import contextlib
import io
import json
from types import SimpleNamespace
import unittest
from r2_handoff_guard import guarded_helper

class GuardTests(unittest.TestCase):
    def run_helper(self, semantic, code, variable):
        spotify=SimpleNamespace(
            show_playlist_library=lambda **kw:[{'song_ids':[1,2,3]}],
            show_liked_songs=lambda **kw:[{'song_id':x} for x in [2,3,4]],
            show_downloaded_songs=lambda **kw:[{'song_id':2}])
        namespace={'apis':SimpleNamespace(spotify=spotify),'access_token':'synthetic',
                   'targets':{1,2,3},'groups':[{'song_ids':[1,2,3]}]}
        generated=guarded_helper('show_playlist_library','song_ids',
            ['intersection'],code,variable,semantic)
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(generated,namespace)
        return json.loads(output.getvalue()),namespace

    def test_semantic_and_guard(self):
        result,_=self.run_helper(True,'for i in targets: pass','targets')
        self.assertEqual(result['selected'],[3])
        self.assertEqual(result['excluded'],[2])

    def test_original_guard_does_not_fix_semantics(self):
        result,_=self.run_helper(False,'for i in targets: pass','targets')
        self.assertEqual(result['selected'],[1,3])

    def test_embedded_assignment_restored_before_guard(self):
        result,_=self.run_helper(False,'pending = groups[0]["song_ids"]\nfor i in pending: pass','pending')
        self.assertEqual(result['selected'],[1,3])

    def test_no_side_effect_api_in_generated_guard(self):
        code=guarded_helper('show_playlist_library','song_ids',
            ['intersection'],'for i in targets: pass','targets',True)
        self.assertNotIn('download_song(',code)
        self.assertNotIn('complete_task(',code)

if __name__=='__main__': unittest.main()
