"""Current-first recognition with chronological domain reduction.

The capture queue owns images. This journal owns interpreted observations only.
Existing reducers decide values and lifecycle. Replay has no file IO; the GUI
installs one complete result. Prefixes before every queued capture are compacted.
"""
from copy import copy,deepcopy


def memory_model(model,fields):
    result=copy(model)
    for field in fields:setattr(result,field,deepcopy(getattr(model,field)))
    result.save=lambda:None
    return result


class ObservationTimeline:
    def __init__(self,run,account):
        self.base_run=memory_model(run,('state',))
        self.base_account=memory_model(account,('records','issues'))
        self.run=self.base_run;self.account=self.base_account
        self.pending={};self.committed_seq=0

    def prepare(self,observation,seq,oldest_pending):
        candidate=copy(self);candidate.pending=dict(self.pending)
        if seq>self.committed_seq:
            candidate.pending[seq]=(deepcopy(observation.get('run')),deepcopy(observation.get('operator')),observation['captured_at'])
        run=memory_model(self.base_run,('state',));account=memory_model(self.base_account,('records','issues'))
        for key,(run_read,operator_read,at)in sorted(candidate.pending.items()):
            if run_read:run.apply(run_read,at)
            if operator_read:account.observe(operator_read,at)
            if oldest_pending is None or key<oldest_pending:
                candidate.base_run=memory_model(run,('state',))
                candidate.base_account=memory_model(account,('records','issues'))
                candidate.committed_seq=key
        candidate.pending={key:value for key,value in candidate.pending.items()if key>candidate.committed_seq}
        candidate.run=run;candidate.account=account
        return candidate

    def commit(self,run,account):
        run_changed=self.run.state!=run.state
        account_changed=self.account.records!=account.records or self.account.issues!=account.issues
        if run_changed:
            run.state=deepcopy(self.run.state);run.save()
        if account_changed:
            account.records=deepcopy(self.account.records);account.issues=deepcopy(self.account.issues)
            account.preserve_original=account.preserve_original or self.account.preserve_original
            account.save()
        return run_changed,account_changed
