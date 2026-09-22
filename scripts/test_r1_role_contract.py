"""Synthetic invariant tests. These are not benchmark results."""
import ast
import unittest
from r1_role_contract_core import Contract, evaluate, first_consumer_boundary
from r1_role_contract_core import replace_handoff, library_adapter

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.record = {'source':[1,2], 'predicate':[2,3], 'selected':[2], 'entity_type':'song'}
        self.c = Contract.fit([self.record], 'fixture-sha')

    def test_identifies_intersection(self):
        self.assertEqual(self.c.hypotheses, ('intersection',))

    def test_new_values_not_memorized(self):
        self.assertEqual(self.c.qualify([8,9],[9,10],entity_type='song',covered=True)['selected'], [9])

    def test_type_mismatch_unknown(self):
        self.assertEqual(self.c.qualify([1],[1],entity_type='album',covered=True)['status'],'UNKNOWN')

    def test_uncovered_unknown(self):
        self.assertEqual(self.c.qualify([1],[1],entity_type='song',covered=False)['status'],'UNKNOWN')

    def test_empty_source_rejected(self):
        with self.assertRaises(ValueError): Contract.fit([], 'x')

    def test_inconsistent_unknown(self):
        c=Contract.fit([{**self.record,'selected':[99]}],'x')
        self.assertEqual(c.qualify([1],[1],entity_type='song',covered=True)['status'],'UNKNOWN')

    def test_ambiguous_source_disagrees_later(self):
        r={'source':[1], 'predicate':[1], 'selected':[1], 'entity_type':'song'}
        c=Contract.fit([r],'x')
        self.assertGreater(len(c.hypotheses),1)
        self.assertEqual(c.qualify([2],[3],entity_type='song',covered=True)['status'],'UNKNOWN')

    def test_same_ambiguous_state_supported_not_certified(self):
        r={'source':[1], 'predicate':[1], 'selected':[1], 'entity_type':'song'}
        self.assertEqual(Contract.fit([r],'x').qualify([2],[2],entity_type='song',covered=True)['status'], 'SUPPORTED_IN_GRAMMAR')

    def test_unknown_program_rejected(self):
        with self.assertRaises(ValueError): evaluate('__import__',[],[])

    def test_patch_overwrite_assignment_only(self):
        code='targets = groups[0]["song_ids"]\nfor i in targets:\n apis.spotify.download_song(song_id=i, access_token=token)'
        changed=replace_handoff(code,'targets')
        before=ast.parse(code); after=ast.parse(changed)
        self.assertEqual(ast.dump(before.body[1]),ast.dump(after.body[1]))
        self.assertEqual(ast.unparse(after.body[0].value),'role_handoff_ids')

    def test_existing_state_assignment_inserted(self):
        code='for i in sorted(targets):\n apis.spotify.download_song(song_id=i, access_token=token)'
        self.assertEqual(first_consumer_boundary([{'code':code}]),(0,'targets'))
        self.assertEqual(len(ast.parse(replace_handoff(code,'targets')).body),2)

    def test_adapter_uses_public_text(self):
        self.assertEqual(library_adapter('from my album library'),('show_album_library','song_ids'))
        with self.assertRaises(ValueError): library_adapter('task 3ab5b8b_3')

if __name__ == '__main__': unittest.main()
