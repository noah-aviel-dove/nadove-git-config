import os
from pathlib import Path
import shlex
import subprocess
import tempfile
from typing import (
    AbstractSet,
    Dict,
    List,
    Optional,
    Sequence,
    Union,
)
import unittest
from unittest import (
    TestCase,
    TestLoader,
)

test_dir = Path(__file__).parent.absolute()
project_root = test_dir.parent


def alias_test(alias):
    def wrapper(method):
        try:
            aliases = method.aliases
        except AttributeError:
            aliases = method.aliases = set()
        aliases.add(alias)
        return method

    return wrapper


class Command:

    def __init__(self, *args: Optional[str]):
        self.args = [arg for arg in args if arg is not None]

    def exec(self) -> subprocess.CompletedProcess:
        return subprocess.run(self.args)

    def exec_out(self) -> bytes:
        return subprocess.check_output(self.args)


class GitAliasTestCase(TestCase):
    class GitCommand(Command):

        def __init__(self, test_case: 'GitAliasTestCase', *args: Optional[str]):
            super().__init__('git', *args)
            self.test_case = test_case

        def assertOutput(self, expected: Union[str, bytes]):
            if isinstance(expected, str):
                expected = expected.encode('UTF8')
            self.test_case.assertEqual(expected, self.exec_out())

    def git_command(self, *args):
        return self.GitCommand(self, *args)

    temp_dir = None

    init_branch = 'test_main'
    child_branches = ['foo', 'bar', 'baz', 'quux']

    @property
    def setup_branches(self) -> List[str]:
        return [self.init_branch, *self.child_branches]

    @classmethod
    def _setup(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        Command('bash', str(test_dir / 'setup.sh'), cls.temp_dir.name).exec()
        os.chdir(cls.temp_dir.name)

    @classmethod
    def _teardown(cls):
        del cls.temp_dir
        os.chdir(test_dir)

    def assertOutputsEqual(self, cmd1: Command, cmd2: Command):
        self.assertEqual(cmd1.exec_out(), cmd2.exec_out())

    def assertGitOutputsEqual(self, args1: Sequence[Optional[str]], args2: Sequence[Optional[str]]):
        self.assertOutputsEqual(self.git_command(*args1), self.git_command(*args2))

    def current_git_branch(self) -> bytes:
        return self.git_command('rev-parse', '--abbrev-ref', '@').exec_out()

    def previous_git_branch(self) -> bytes:
        return self.git_command('rev-parse', '--abbrev-ref', '@{-1}').exec_out()

    def assertBranch(self, branch: str):
        self.git_command('b').assertOutput(f'{branch}\n')


class ReadOnlyGitAliasTestCase(GitAliasTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls._setup()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._teardown()


class ReadWriteGitAliasTestCase(GitAliasTestCase):

    def setUp(self) -> None:
        self._setup()

    def tearDown(self) -> None:
        self._teardown()


class TestLocalInfo(ReadOnlyGitAliasTestCase):

    @alias_test('rev')
    @alias_test('rev8')
    def test_parsing(self):
        for ref in [None, '@', '@^', '@{-1}', *self.setup_branches]:
            expected_output = self.git_command('rev-parse', '@' if ref is None else ref).exec_out()
            with self.subTest(ref=ref, cmd='rev'):
                self.git_command('rev', ref).assertOutput(expected_output)
            with self.subTest(ref=ref, cmd='rev8'):
                self.git_command('rev8', ref).assertOutput(expected_output[:8] + b'\n')

    @alias_test('s')
    def test_status(self):
        self.assertOutputsEqual(self.git_command('status', '-sb'),
                                self.git_command('s'))

    @alias_test('h')
    @alias_test('h1')
    @alias_test('l')
    @alias_test('l1')
    @alias_test('lg')
    def test_log(self):
        for alias_cmd, stock_cmd in [
            ('h', 'log --pretty=%h'),
            ('h -n1', 'log -n1 --pretty=%h'),
            ('h1', 'log -n1 --pretty=%h'),
            ('l', 'log --oneline'),
            ('l -n1', 'log -n1 --oneline'),
            ('l1', 'log -n1 --oneline'),
            ('lg', 'log --oneline --graph')
        ]:
            with self.subTest(alias=alias_cmd):
                self.assertGitOutputsEqual(shlex.split(stock_cmd),
                                           shlex.split(stock_cmd))

    @alias_test('b')
    def test_branch(self):
        self.assertBranch(self.init_branch)
        for ref, branch in [('', self.init_branch),
                            ('@', self.init_branch),
                            *[(branch, branch) for branch in self.setup_branches]]:
            with self.subTest(ref):
                self.git_command('b', ref).assertOutput(f'{branch}\n')
        prev_branch = self.previous_git_branch()
        for ref in ['-', '@{-1}']:
            with self.subTest(ref):
                self.git_command('b', ref).assertOutput(prev_branch)

    @alias_test('bll')
    def test_local_branch_list(self):
        self.git_command('bll').assertOutput('\n'.join([
            *[f'  {branch}' for branch in sorted(self.child_branches)],
            f'* {self.init_branch}\n'
        ]))

    @alias_test('bllg')
    def test_grep_local_branch(self):

        def expected_output(branches, current_branch):
            return '\n'.join(
                f'{"*" if branch == current_branch else " "} {branch}'
                for branch in branches
            ) + '\n'

        for pattern, expected_matches in [
            (None, sorted(self.setup_branches)),
            ('foo', ['foo']),
            ('ba[rz]', ['bar', 'baz']),
            ('*', ['test_main'])
        ]:
            with self.subTest(f'{expected_matches} =~ {pattern}'):
                self.git_command('bllg', pattern).assertOutput(expected_output(expected_matches, self.init_branch))

    @alias_test('dr')
    def test_show(self):
        for ref in [None, '@', '@^', *self.setup_branches]:
            with self.subTest(ref=ref):
                self.assertGitOutputsEqual(['show', '--oneline', ref],
                                           ['dr', ref])
        with self.subTest(ref='-'):
            self.assertGitOutputsEqual(['show', '--oneline', '@{-1}'],
                                       ['dr', '-'])


class TestLocalReadWrite(ReadWriteGitAliasTestCase):

    @alias_test('co')
    def test_checkout(self):
        self.assertBranch(self.init_branch)
        branches = self.setup_branches
        for branch in self.setup_branches:
            self.git_command('co', branch).exec()
            self.assertBranch(branch)
            if branch == self.init_branch:
                self.assertRaises(FileNotFoundError, lambda: open('c.txt'))
            else:
                with open('c.txt') as f:
                    self.assertEqual([f'Editing on branch {branch}\n'], f.readlines())
        
        swap = self.git_command('co', '-')
        for i in [-2, -1]:
            swap.exec()
            self.assertBranch(branches[i])
        
        self.git_command('co', '@^').exec()
        self.assertBranch('HEAD')
        swap.exec()
        self.assertBranch(branches[i])


    @alias_test('d')
    @alias_test('dd')
    @alias_test('ds')
    @alias_test('a')
    @alias_test('au')
    @alias_test('r')
    def test_dirtiness(self):
        d = self.git_command('d')
        dd = self.git_command('dd')
        ds = self.git_command('ds')
        r = self.git_command('r')
        for cmd in [d, dd, ds]:
            cmd.assertOutput('\n')
        for f in 'ab':
            Command(['bash', '-c', f'echo overwrite {f}.txt >{f}.txt']).exec()
        self.assertGitCommandOutputsEqual(['d'], ['diff'])
        self.assertGitCommandOutputsEqual(['dd'], ['diff'])
        ds.assertOutput('\n')
        self.git_command('a a.txt').assertOutput('a.txt')
        dd.assertOutput('\n')
        self.assertGitCommandOutputsEqual(['ds'], ['diff', '--staged'])
        self.assertGitCommandOutputsEqual(['d'], ['ds'])
        r.assertOutput('Unstaged changes after reset:\nM\ta.txt\n')
        self.git_command('au').assertOutput('a.txt\nb.txt\n')
        

        

# FIXME https://github.com/noah-aviel-dove/nadove-git-aliases/issues/20
@unittest.skip('Tests involving a remote repository are not implemented')
class TestRemote(GitAliasTestCase):

    @alias_test('bu')
    @alias_test('du')
    @alias_test('dul')
    @alias_test('ru')
    @alias_test('rhu')
    @alias_test('dru')
    @alias_test('p')
    @alias_test('pf')
    @alias_test('pu')
    @alias_test('pd')
    @alias_test('p')
    @alias_test('rhp')
    @alias_test('rhpf')
    @alias_test('rhpfc')
    @alias_test('rhpfci')
    @alias_test('mf')
    @alias_test('f')
    @alias_test('ff')
    @alias_test('fs')
    @alias_test('frhu')
    def test(self):
        raise NotImplementedError


class Meta(TestCase):
    base_test_cls = GitAliasTestCase

    def load_aliases(self) -> Dict[str, str]:
        aliases = {}
        with open(project_root / 'alias.gitconfig') as f:
            for line in f:
                alias, _, definition = line.rstrip().partition(" = ")
                aliases[alias] = definition
        return aliases

    def load_test_names(self) -> AbstractSet[str]:
        loader = TestLoader()
        return set.union(*(
            self.get_test_method_aliases(test)
            for suite in loader.loadTestsFromName(__name__)
            for test in suite
            if isinstance(test, self.base_test_cls)
        ))

    def get_test_method_aliases(self, test: TestCase) -> AbstractSet[str]:
        test_id = test.id()
        _, _, method_name = test_id.rpartition('.')
        method = getattr(test, method_name)
        try:
            return method.aliases
        except AttributeError:
            raise RuntimeError(f'{test_id} is not mapped to any aliases')

    def test_coverage(self):
        self.assertSetEqual(set(self.load_aliases().keys()),
                            self.load_test_names())
