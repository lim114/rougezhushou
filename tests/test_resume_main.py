"""Exercise branch recovery against a local bare repository, without installation."""
from pathlib import Path
import os,shutil,subprocess,tempfile,unittest

ROOT=Path(__file__).resolve().parents[1]

class ResumeMainTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='resume-main-',dir=ROOT/'.cache');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.remote=self.root/'remote.git';self.seed=self.root/'seed';self.work=self.root/'work'
        self.bash=Path(shutil.which('bash') or Path(shutil.which('git')).parent.parent/'usr/bin/sh.exe')
        self.assertTrue(self.bash.is_file())
        self.assertIn('GNU bash',subprocess.check_output([str(self.bash),'--version']).decode('utf8'))
        self.git(self.root,'init','--bare','--initial-branch=main',str(self.remote))
        self.seed.mkdir();self.git(self.seed,'init','--initial-branch=main')
        self.configure(self.seed)
        (self.seed/'.gitignore').write_text('.venv/\n','utf8')
        (self.seed/'scripts').mkdir();shutil.copyfile(ROOT/'scripts/resume_development.sh',self.seed/'scripts/resume_development.sh')
        (self.seed/'state.txt').write_text('baseline','utf8')
        self.git(self.seed,'add','.');self.git(self.seed,'commit','-m','baseline')
        self.git(self.seed,'remote','add','origin',str(self.remote));self.git(self.seed,'push','-u','origin','main')
        self.git(self.root,'clone',str(self.remote),str(self.work));self.configure(self.work)
        executable=self.work/'.venv/bin/python';executable.parent.mkdir(parents=True)
        executable.write_text('#!/bin/sh\nprintf "%s\\n" "$*" > .venv/check-called\n','utf8',newline='\n')
        executable.chmod(0o755)

    def git(self,cwd,*args):
        return subprocess.check_output(['git',*args],cwd=cwd,stderr=subprocess.PIPE).decode('utf8').strip()

    def configure(self,cwd):
        self.git(cwd,'config','user.name','Isolated test');self.git(cwd,'config','user.email','isolated@example.invalid')

    def advance_remote(self):
        (self.seed/'remote.txt').write_text('new upstream data','utf8')
        self.git(self.seed,'add','remote.txt');self.git(self.seed,'commit','-m','advance main');self.git(self.seed,'push','origin','main')
        return self.git(self.seed,'rev-parse','HEAD')

    def resume(self):
        return subprocess.run([str(self.bash),'scripts/resume_development.sh'],cwd=self.work,
                              stdout=subprocess.PIPE,stderr=subprocess.PIPE)

    def test_recovers_main_and_fast_forwards_without_retired_remote_branch(self):
        self.git(self.work,'switch','-c','cloud-worker');new=self.advance_remote()
        result=self.resume();self.assertEqual(result.returncode,0,result.stderr.decode('utf8'))
        self.assertEqual(self.git(self.work,'branch','--show-current'),'main')
        self.assertEqual(self.git(self.work,'rev-parse','HEAD'),new)
        self.assertEqual((self.work/'.venv/check-called').read_text('utf8').strip(),'-m pip check')
        self.assertNotIn('codex/p2-development',self.git(self.work,'branch','-r'))

    def test_dirty_checkout_is_preserved_before_switch(self):
        self.git(self.work,'switch','-c','cloud-worker');(self.work/'state.txt').write_text('uncommitted','utf8')
        prior_remote=self.git(self.work,'rev-parse','origin/main');self.advance_remote()
        result=self.resume();self.assertNotEqual(result.returncode,0)
        self.assertEqual(self.git(self.work,'branch','--show-current'),'cloud-worker')
        self.assertEqual((self.work/'state.txt').read_text('utf8'),'uncommitted')
        self.assertEqual(self.git(self.work,'rev-parse','origin/main'),prior_remote)
        self.assertFalse((self.work/'.venv/check-called').exists())

    def test_diverged_main_is_not_reset_or_merged_automatically(self):
        (self.work/'local.txt').write_text('local commit','utf8')
        self.git(self.work,'add','local.txt');self.git(self.work,'commit','-m','local divergence')
        before=self.git(self.work,'rev-parse','HEAD');new=self.advance_remote()
        result=self.resume();self.assertNotEqual(result.returncode,0)
        self.assertEqual(self.git(self.work,'rev-parse','HEAD'),before)
        self.assertEqual(self.git(self.work,'rev-parse','origin/main'),new)
        self.assertEqual((self.work/'local.txt').read_text('utf8'),'local commit')
        self.assertFalse((self.work/'.venv/check-called').exists())

if __name__=='__main__':unittest.main()
