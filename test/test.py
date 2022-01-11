import os
from pathlib import Path
import shlex
import subprocess
import tempfile
from typing import (
    Dict,
    FrozenSet,
)
from unittest import (
    TestCase,
    TestLoader,
)


def alias_test(alias):
    def wrapper(method):
        method.alias = alias
        return method

    return wrapper


class Shell:

    def exec(self, *cmd: str) -> subprocess.CompletedProcess:
        return subprocess.run(cmd)

    def exec_out(self, *cmd: str) -> bytes:
        return subprocess.check_output(cmd)

    def exec_git(self, *cmd: str) -> subprocess.CompletedProcess:
        return self.exec('git', *cmd)

    def exec_git_out(self, *cmd: str) -> bytes:
        return self.exec_out('git', *cmd)


class GitAliasTestCase(TestCase, Shell):
    test_dir = Path(__file__).parent.absolute()
    temp_dir = None

    @classmethod
    def setUpClass(cls):
        assert os.getcwd() == str(cls.test_dir)
        cls.temp_dir = tempfile.TemporaryDirectory()
        Shell().exec('bash', './setup.sh', cls.temp_dir.name)
        os.chdir(cls.temp_dir.name)

    @classmethod
    def tearDownClass(cls):
        del cls.temp_dir
        os.chdir(cls.test_dir)

    def test(self):
        print('hello world!')

    def assertGitCommandOutput(self, cmd: str, expected_output: bytes):
        actual = self.exec_git_out(*shlex.split(cmd))
        self.assertEqual(expected_output, actual)

    def assertGitCommandOutputsEqual(self, alias_cmd: str, stock_cmd: str):
        expected = self.exec_git_out(*shlex.split(stock_cmd))
        self.assertGitCommandOutput(alias_cmd, expected)


class TestInfo(GitAliasTestCase):

    @alias_test('b')
    def test_branch_resolution(self):
        self.assertGitCommandOutput('b', b'test_main\n')

    @alias_test('h')
    @alias_test('h1')
    def test_hash(self):
        self.assertGitCommandOutputsEqual('h', 'log --pretty=%h')
        self.assertGitCommandOutputsEqual('h -n1', 'log -n1 --pretty=%h')
        self.assertGitCommandOutputsEqual('h1', 'log -n1 --pretty=%h')

    @alias_test('l')
    @alias_test('l1')
    def test_log(self):
        self.assertGitCommandOutputsEqual('l', 'log --oneline')
        self.assertGitCommandOutputsEqual('l -n1', 'log -n1 --oneline')
        self.assertGitCommandOutputsEqual('l1', 'log -n1 --oneline')


class RemoteTest(GitAliasTestCase):

    @alias_test('p')
    @alias_test('pf')
    @alias_test('pu')
    @alias_test('pd')
    @alias_test('p')
    @alias_test('rhp')
    @alias_test('rhpf')
    @alias_test('rhpfc')
    @alias_test('rhpfci')
    @alias_test('f')
    @alias_test('ff')
    @alias_test('fs')
    @alias_test('frhu')
    def test(self):
        # FIXME https://github.com/noah-aviel-dove/nadove-git-aliases/issues/20
        pass


class Meta(TestCase):
    base_test_cls = GitAliasTestCase

    def load_aliases(self) -> Dict[str, str]:
        aliases = {}
        with open('alias.gitconfig') as f:
            for line in f:
                alias, _, definition = line.rstrip().partition(" = ")
                aliases[alias] = definition
        return aliases

    def load_test_names(self) -> FrozenSet[str]:
        loader = TestLoader()
        return frozenset(
            self.get_test_method_alias(test)
            for suite in loader.loadTestsFromName(__name__)
            for test in suite
            if isinstance(test, self.base_test_cls)
        )

    def get_test_method_alias(self, test: TestCase) -> str:
        _, _, method_name = test.id().rpartition('.')
        return getattr(test, method_name).alias

    def test_coverage(self):
        self.assertSetEqual(set(self.load_aliases().keys()),
                            self.load_test_names())
