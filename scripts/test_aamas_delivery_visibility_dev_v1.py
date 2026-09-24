import copy
import unittest

import aamas_delivery_visibility_dev_v1 as pair


class PairedVisibilityContractTest(unittest.TestCase):
    def setUp(self):
        self.secrets = pair.base.Secrets()
        self.plan = {'plan_status':'ready','planned_actions':[],
                     'review_reason':'Public task data reviewed; no task write is justified.',
                     'uncertainties':[], 'delivery_assessment':'not_available',
                     'intended_delivery_use':None}
        self.reads = [{'step':1,'public_task_data_reads':1}]

    def test_hidden_ready_empty_requires_public_read(self):
        self.assertEqual(pair.validate_plan(self.plan,self.reads,'hidden',self.secrets),
                         self.plan)
        with self.assertRaises(pair.a0.ArtifactInvalid):
            pair.validate_plan(self.plan,[],'hidden',self.secrets)

    def test_both_arms_can_seal_unknown_without_fabricated_action(self):
        for arm in ('hidden','visible'):
            plan = copy.deepcopy(self.plan)
            plan['plan_status']='unknown'
            plan['review_reason']='Evidence is insufficient.'
            plan['uncertainties']=['Recipient cannot be verified.']
            plan['delivery_assessment'] = ('not_available' if arm=='hidden' else 'unknown')
            self.assertEqual(pair.validate_plan(plan,[],arm,self.secrets),plan)

    def test_ready_action_needs_own_successful_task_data_read(self):
        plan=copy.deepcopy(self.plan)
        plan['planned_actions']=[{'app':'venmo','api':'create_payment_request',
            'non_secret_arguments':{'amount':32.0},'public_source_steps':[2]}]
        with self.assertRaises(pair.a0.ArtifactInvalid):
            pair.validate_plan(plan,self.reads,'hidden',self.secrets)
        plan['planned_actions'][0]['public_source_steps']=[1]
        self.assertEqual(pair.validate_plan(plan,self.reads,'hidden',self.secrets),plan)

    def test_plan_api_match_separates_attempt_and_success(self):
        plan=copy.deepcopy(self.plan)
        plan['planned_actions']=[{'app':'venmo','api':'create_payment_request',
            'non_secret_arguments':{'amount':32.0,'user_email':'a@example.com'},
            'public_source_steps':[1]}]
        audit=[{'origin':'actor','method':'post','api_path':'/venmo/requests',
                'app':'venmo','api':'create_payment_request','ok':False,
                'arguments':{'amount':32.0,'user_email':'a@example.com'}}]
        use=pair.action_use(plan,audit,self.secrets)
        self.assertEqual(use['exact_planned_attempted_action_matches'],[0])
        self.assertEqual(use['matched_api_success_planned_action_indices'],[])

    def test_old_proposal_match_is_one_to_one_and_reports_changes(self):
        proposal={'requests':[{'recipient_email':'a@example.com','amount_usd':32.0},
                              {'recipient_email':'a@example.com','amount_usd':32.0},
                              {'recipient_email':'b@example.com','amount_usd':32.0}]}
        def call(email,amount):
            return {'app':'venmo','api':'create_payment_request','ok':True,
                    'arguments':{'user_email':email,'amount':amount,
                                 'description':'I paid for cable bill.'}}
        use={'actor_task_write_calls':[call('a@example.com',32.0),
                                       call('b@example.com',31.0)]}
        match=pair.historical_proposal_row_audit(proposal,use)
        self.assertEqual(len(match['exact_attempted_proposal_row_matches']),1)
        self.assertEqual(len(match['same_recipient_modified_writes']),1)
        self.assertEqual(match['unmatched_proposal_row_indices'],[1])
        self.assertTrue(match['content_overlap_is_not_causal_proof_of_delivery_use'])

    def test_final_config_requires_exact_preflight_receipts(self):
        cfg=pair.config(parent_validation=False)
        self.assertEqual(cfg['status'],'FROZEN_PROSPECTIVE_PAIRED_DEV_V1')
        self.assertEqual(cfg['caps']['global_new_task_attempts'],52)
        self.assertEqual(cfg['arm_order'],['visible','hidden'])
        self.assertEqual(set(cfg['preflight']),{
            'native_fixture_path','provider_health_path',
            'native_fixture_llm_calls','provider_health_llm_attempt_cap'})


if __name__=='__main__':
    unittest.main()
