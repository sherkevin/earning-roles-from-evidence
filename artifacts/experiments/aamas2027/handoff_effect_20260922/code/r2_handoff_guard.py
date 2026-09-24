"""Consumer-state intervention. Guard label must come from frozen proposal."""
from __future__ import annotations
import ast
from r1_native_replay import helper_code as semantic_helper

def guarded_helper(endpoint, field, hypotheses, code, variable, semantic):
    if semantic:
        prefix=semantic_helper(endpoint,field,hypotheses)
        # Preserve all source operations but emit only the final audit record.
        prefix=prefix[:prefix.rfind('print(json.dumps(')]
        selection='role_handoff_ids'
    else:
        tree=ast.parse(code)
        assignments=[n for n in tree.body if isinstance(n,ast.Assign) and
            any(isinstance(t,ast.Name) and t.id==variable for t in n.targets)]
        if len(assignments)>1: raise ValueError('Ambiguous original selection')
        prefix='import json\n'
        if assignments: prefix += ast.unparse(assignments[0])+'\n'
        selection=variable
    prefix += f'\n_r2_semantic_targets = set({selection})\n'
    return prefix + '''_r2_downloaded = []
for _r2_page in range(100):
    _r2_batch = apis.spotify.show_downloaded_songs(access_token=access_token, page_index=_r2_page, page_limit=20)
    _r2_downloaded.extend(_r2_batch)
    if len(_r2_batch) < 20:
        break
else:
    raise RuntimeError("R2 pagination cap; UNKNOWN")
_r2_done = {r['song_id'] for r in _r2_downloaded}
role_handoff_ids = sorted(_r2_semantic_targets - _r2_done)
print(json.dumps({"semantic_targets": sorted(_r2_semantic_targets), "already_done": sorted(_r2_done), "selected": role_handoff_ids, "excluded": sorted(_r2_semantic_targets & _r2_done)}))
'''
