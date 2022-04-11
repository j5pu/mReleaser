#!/usr/bin/env python3
# coding=utf-8
"""
Mreleaser __init__.py Module
"""
from __future__ import annotations
__all__ = (
    "AnyPath",
    "ExcType",
    "TemporaryFileType",

    "CmdError",
    "Env",
    "Git",
    "Path",
    "Releaser",
    "TempDir",
    "aiocmd",
    "cli_invoke",
    "cmd",
    "suppress",
    "version",
)
import asyncio
import contextlib
import ipaddress
import importlib.metadata
import os
import pathlib
import subprocess
import tempfile
import urllib.parse
from dataclasses import dataclass
from dataclasses import field
from dataclasses import InitVar
from ipaddress import IPv4Address
from ipaddress import IPv6Address
from os import PathLike
from subprocess import CompletedProcess
from typing import Any
from typing import AnyStr
from typing import Callable
from typing import ClassVar
from typing import IO
from typing import Literal
from typing import Optional
from typing import ParamSpec
from typing import Type
from typing import TypeAlias
from typing import TypeVar
from typing import Union
from urllib.parse import ParseResult

import git
from git import Git as GitCmd
from git import GitCmdObjectDB
from gitdb import LooseObjectDB
from ppath import Path
from setuptools.config import read_configuration
from typer import Argument
from typer import Typer
from typer.testing import CliRunner

P = ParamSpec('P')
T = TypeVar('T')

GitType: TypeAlias = 'Git'
PathType: TypeAlias = 'Path'

__project__: str = pathlib.Path(__file__).parent.name
app = Typer(add_completion=False, context_settings=dict(help_option_names=['-h', '--help']), name=__project__)

AnyPath: TypeAlias = Union[PathType, PathLike, AnyStr, IO[AnyStr]]
ExcType: TypeAlias = Type[Exception] | tuple[Type[Exception], ...]
class TemporaryFileType(type(tempfile.NamedTemporaryFile())): file: PathType = None


class CmdError(subprocess.CalledProcessError):
    """
    Raised when run() and the process returns a non-zero exit status.

    Attributes:
      process: The CompletedProcess object returned by run().
    """
    def __init__(self, process: CompletedProcess = None):
        super().__init__(process.returncode, process.args, output=process.stdout, stderr=process.stderr)

    def __str__(self):
        value = super().__str__()
        if self.stderr is not None:
            value += "\n" + self.stderr
        if self.stdout is not None:
            value += "\n" + self.stdout
        return value


@dataclass
class Env:
    # noinspection LongLine
    """
    GitHub Actions Variables Class

    See Also: `Environment variables
    <https://docs.github.com/en/enterprise-cloud@latest/actions/learn-github-actions/environment-variables>`_

    If you need to use a workflow run's URL from within a job, you can combine these environment variables:
        ``$GITHUB_SERVER_URL/$GITHUB_REPOSITORY/actions/runs/$GITHUB_RUN_ID``

    If you generate a value in one step of a job, you can use the value in subsequent ``steps`` of
        the same job by assigning the value to an existing or new environment variable and then writing
        this to the ``GITHUB_ENV`` environment file, see `Commands
        <https://docs.github.com/en/enterprise-cloud@latest/actions/reference/workflow-commands-for-github-actions/#setting-an-environment-variable>`_.

    If you want to pass a value from a step in one job in a ``workflow`` to a step in another job in the workflow,
        you can define the value as a job output, see `Syntax
        <https://docs.github.com/en/enterprise-cloud@latest/actions/learn-github-actions/workflow-syntax-for-github-actions#jobsjob_idoutputs>`_.
    """
    CI: bool | str | None = field(default=None, init=False)
    """Always set to ``true`` in a GitHub Actions environment."""

    GITHUB_ACTION: str | None = field(default=None, init=False)
    # noinspection LongLine
    """
    The name of the action currently running, or the `id
    <https://docs.github.com/en/enterprise-cloud@latest/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstepsid>`_ of a step. 
    
    For example, for an action, ``__repo-owner_name-of-action-repo``.
    
    GitHub removes special characters, and uses the name ``__run`` when the current step runs a script without an id. 

    If you use the same script or action more than once in the same job, 
    the name will include a suffix that consists of the sequence number preceded by an underscore. 
    
    For example, the first script you run will have the name ``__run``, and the second script will be named ``__run_2``. 

    Similarly, the second invocation of ``actions/checkout`` will be ``actionscheckout2``.
    """

    GITHUB_ACTION_PATH: Path | str | None = field(default=None, init=False)
    """
    The path where an action is located. This property is only supported in composite actions. 
    
    You can use this path to access files located in the same repository as the action. 
    
    For example, ``/home/runner/work/_actions/repo-owner/name-of-action-repo/v1``.
    """

    GITHUB_ACTION_REPOSITORY: str | None = field(default=None, init=False)
    """
    For a step executing an action, this is the owner and repository name of the action. 
    
    For example, ``actions/checkout``.
    """

    GITHUB_ACTIONS: bool | str | None = field(default=None, init=False)
    """
    Always set to ``true`` when GitHub Actions is running the workflow. 
    
    You can use this variable to differentiate when tests are being run locally or by GitHub Actions.
    """

    GITHUB_ACTOR: str | None = field(default=None, init=False)
    """
    The name of the person or app that initiated the workflow. 
    
    For example, ``octocat``.
    """

    GITHUB_API_URL: ParseResult | str | None = field(default=None, init=False)
    """
    API URL. 
    
    For example: ``https://api.github.com``.
    """

    GITHUB_BASE_REF: str | None = field(default=None, init=False)
    """
    The name of the base ref or target branch of the pull request in a workflow run. 
    
    This is only set when the event that triggers a workflow run is either ``pull_request`` or ``pull_request_target``. 
    
    For example, ``main``.
    """

    GITHUB_ENV: Path | str | None = field(default=None, init=False)
    # noinspection LongLine
    """
    The path on the runner to the file that sets environment variables from workflow commands. 
    
    This file is unique to the current step and changes for each step in a job. 
    
    For example, ``/home/runner/work/_temp/_runner_file_commands/set_env_87406d6e-4979-4d42-98e1-3dab1f48b13a``. 
    
    For more information, see `Workflow commands for GitHub Actions.
    <https://docs.github.com/en/enterprise-cloud@latest/actions/using-workflows/workflow-commands-for-github-actions#setting-an-environment-variable>`_
    """

    GITHUB_EVENT_NAME: str | None = field(default=None, init=False)
    """
    The name of the event that triggered the workflow. 
    
    For example, ``workflow_dispatch``.
    """

    GITHUB_EVENT_PATH: Path | str | None = field(default=None, init=False)
    """
    The path to the file on the runner that contains the full event webhook payload. 
    
    For example, ``/github/workflow/event.json``.
    """

    GITHUB_GRAPHQL_URL: ParseResult | str | None = field(default=None, init=False)
    """
    Returns the GraphQL API URL. 
    
    For example: ``https://api.github.com/graphql``.
    """

    GITHUB_HEAD_REF: str | None = field(default=None, init=False)
    """
    The head ref or source branch of the pull request in a workflow run. 
    
    This property is only set when the event that triggers a workflow run is either 
    ``pull_request`` or ``pull_request_target``.
    
    For example, ``feature-branch-1``.
    """

    GITHUB_JOB: str | None = field(default=None, init=False)
    # noinspection LongLine
    """
    The `job_id
    <https://docs.github.com/en/enterprise-cloud@latest/actions/reference/workflow-syntax-for-github-actions#jobsjob_id>`_ 
    of the current job. 
    
    For example, ``greeting_job``.
    """

    GITHUB_PATH: Path | str | None = field(default=None, init=False)
    # noinspection LongLine
    """
    The path on the runner to the file that sets system PATH variables from workflow commands. 
    This file is unique to the current step and changes for each step in a job. 
    
    For example, ``/home/runner/work/_temp/_runner_file_commands/add_path_899b9445-ad4a-400c-aa89-249f18632cf5``. 
    
    For more information, see 
    `Workflow commands for GitHub Actions.
     <https://docs.github.com/en/enterprise-cloud@latest/actions/using-workflows/workflow-commands-for-github-actions#adding-a-system-path>`_
    """

    GITHUB_REF: str | None = field(default=None, init=False)
    """
    The branch or tag ref that triggered the workflow run.
    
    For branches this is the format ``refs/heads/<branch_name>``, 
    for tags it is ``refs/tags/<tag_name>``, 
    and for pull requests it is ``refs/pull/<pr_number>/merge``. 
    
    This variable is only set if a branch or tag is available for the event type. 
    
    For example, ``refs/heads/feature-branch-1``.
    """

    GITHUB_REF_NAME: str | None = field(default=None, init=False)
    """
    The branch or tag name that triggered the workflow run. 
    
    For example, ``feature-branch-1``.
    """

    GITHUB_REF_PROTECTED: bool | str | None = field(default=None, init=False)
    """
    ``true`` if branch protections are configured for the ref that triggered the workflow run.
    """

    GITHUB_REF_TYPE: str | None = field(default=None, init=False)
    """
    The type of ref that triggered the workflow run. 
    
    Valid values are ``branch`` or ``tag``.
    
    For example, ``branch``.
    """

    GITHUB_REPOSITORY: str | None = field(default=None, init=False)
    """
    The owner and repository name. 
    
    For example, ``octocat/Hello-World``.
    """

    GITHUB_REPOSITORY_OWNER: str | None = field(default=None, init=False)
    """
    The repository owner's name. 
    
    For example, ``octocat``.
    """

    GITHUB_RETENTION_DAYS: str | None = field(default=None, init=False)
    """
    The number of days that workflow run logs and artifacts are kept. 
    
    For example, ``90``.
    """

    GITHUB_RUN_ATTEMPT: str | None = field(default=None, init=False)
    """
    A unique number for each attempt of a particular workflow run in a repository. 
    
    This number begins at ``1`` for the workflow run's first attempt, and increments with each re-run.
    
    For example, ``3``.
    """

    GITHUB_RUN_ID: str | None = field(default=None, init=False)
    """
    A unique number for each workflow run within a repository. 
    
    This number does not change if you re-run the workflow run. 
    
    For example, ``1658821493``.
    """

    GITHUB_RUN_NUMBER: str | None = field(default=None, init=False)
    """
    A unique number for each run of a particular workflow in a repository. 
    
    This number begins at ``1`` for the workflow's first run, and increments with each new run. 
    This number does not change if you re-run the workflow run.

    For example, ``3``.
    """

    GITHUB_SERVER_URL: ParseResult | str | None = field(default=None, init=False)
    """
    The URL of the GitHub Enterprise Cloud server. 
    
    For example: ``https://github.com``.
    """

    GITHUB_SHA: str | None = field(default=None, init=False)
    """
    The commit SHA that triggered the workflow. 
    
    The value of this commit SHA depends on the event that triggered the workflow.
    For more information, see `Events that trigger workflows. 
    <https://docs.github.com/en/enterprise-cloud@latest/actions/using-workflows/events-that-trigger-workflows>`_ 

    For example, ``ffac537e6cbbf934b08745a378932722df287a53``.
    """

    GITHUB_WORKFLOW: Path | str | None = field(default=None, init=False)
    """
    The name of the workflow. 
    
    For example, ``My test workflow``. 
    
    If the workflow file doesn't specify a name, 
    the value of this variable is the full path of the workflow file in the repository.
    """

    GITHUB_WORKSPACE: Path | str | None = field(default=None, init=False)
    """
    The default working directory on the runner for steps, and the default location of your repository 
    when using the `checkout <https://github.com/actions/checkout>`_ action. 
    
    For example, ``/home/runner/work/my-repo-name/my-repo-name``.
    """

    RUNNER_ARCH: str | None = field(default=None, init=False)
    """
    The architecture of the runner executing the job. 
    
    Possible values are ``X86``, ``X64``, ``ARM``, or ``ARM64``.
    
    For example, ``X86``.
    """

    RUNNER_NAME: str | None = field(default=None, init=False)
    """
    The name of the runner executing the job. 
    
    For example, ``Hosted Agent``.
    """

    RUNNER_OS: str | None = field(default=None, init=False)
    """
    The operating system of the runner executing the job. 
    
    Possible values are ``Linux``, ``Windows``, or ``macOS``. 
    
    For example, ``Linux``.
    """

    RUNNER_TEMP: Path | str | None = field(default=None, init=False)
    """
    The path to a temporary directory on the runner. 
    
    This directory is emptied at the beginning and end of each job. 
    
    Note that files will not be removed if the runner's user account does not have permission to delete them. 
    
    For example, ``_temp``.
    """

    RUNNER_TOOL_CACHE: str | None = field(default=None, init=False)
    # noinspection LongLine
    """
    The path to the directory containing preinstalled tools for GitHub-hosted runners. 
    
    For more information, see `About GitHub-hosted runners. 
    <https://docs.github.com/en/enterprise-cloud@latest/actions/reference/specifications-for-github-hosted-runners/#supported-software>`_
    
    `Ubuntu latest <https://github.com/actions/virtual-environments/blob/main/images/linux/Ubuntu2004-Readme.md>`_ 
    `macOS latest <https://github.com/actions/virtual-environments/blob/main/images/macos/macos-11-Readme.md>`_

    For example, ``C:\hostedtoolcache\windows``.
    """

    SUDO_USER: str | None = field(default=None, init=False)
    HOME: str | None = field(default=None, init=False)
    LC_TYPE: str | None = field(default=None, init=False)
    PYTHONUNBUFFERED: str | None = field(default=None, init=False)
    XPC_FLAGS: str | None = field(default=None, init=False)
    SSH_AUTH_SOCK: str | None = field(default=None, init=False)
    TMPDIR: str | None = field(default=None, init=False)
    IPYTHONENABLE: str | None = field(default=None, init=False)
    OLDPWD: str | None = field(default=None, init=False)
    PYTHONIOENCODING: str | None = field(default=None, init=False)
    SHELL: str | None = field(default=None, init=False)
    PYTHONPATH: str | None = field(default=None, init=False)
    PYCHARM_MATPLOTLIB_INTERACTIVE: str | None = field(default=None, init=False)
    __CFBundleIdentifier: str | None = field(default=None, init=False)
    __CF_USER_TEXT_ENCODING: str | None = field(default=None, init=False)
    PYCHARM_DISPLAY_PORT: str | None = field(default=None, init=False)
    PYCHARM_HOSTED: str | None = field(default=None, init=False)
    PWD: str | None = field(default=None, init=False)
    XPC_SERVICE_NAME: str | None = field(default=None, init=False)
    PYCHARM_MATPLOTLIB_INDEX: str | None = field(default=None, init=False)
    LOGNAME: str | None = field(default=None, init=False)
    PYDEVD_LOAD_VALUES_ASYNC: str | None = field(default=None, init=False)
    PYCHARM_PROPERTIES: str | None = field(default=None, init=False)
    PS1: str | None = field(default=None, init=False)
    COMMAND_MODE: str | None = field(default=None, init=False)
    PYCHARM_VM_OPTIONS: str | None = field(default=None, init=False)
    PATH: str | None = field(default=None, init=False)

    _parse_as_int: ClassVar[tuple[str, ...]] = ("GITHUB_RUN_ATTEMPT", "GITHUB_RUN_ID", "GITHUB_RUN_NUMBER",)
    _parse_as_int_suffix: ClassVar[tuple[str, ...]] = ("_GID", "_JOBS", "_PORT", "_UID",)
    parsed: InitVar[bool] = True

    def __post_init__(self, parsed: bool) -> None:
        """
        Instance of Env class

        Args:
            parsed: Parse the environment variables using :func:`mreleaser.parse_str`,
                except :func:`Env.as_int` (default: True)
        """
        self.__dict__.update({k: self.as_int(k, v) for k, v in os.environ.items()} if parsed else os.environ)

    def __contains__(self, item):
        return item in self.__dict__

    def __getattr__(self, name: str) -> str | None:
        if name in self:
            return self.__dict__[name]
        return None

    def __getattribute__(self, name: str) -> str | None:
        if hasattr(self, name):
            return super().__getattribute__(name)
        return None

    def __getitem__(self, item: str) -> str | None:
        return self.__getattr__(item)

    @classmethod
    def as_int(cls, key: str, value: str = "") -> bool | Path | ParseResult | IPv4Address | IPv6Address | int | str:
        """
        Parse as int if environment variable should be forced to be parsed as int checking if:

            - has value,
            - key in :data:`Env._parse_as_int` or
            - key ends with one of the items in :data:`Env._parse_as_int_suffix`.

        Args
            key: Environment variable name.
            value: Environment variable value (default: "").

        Returns:
            int, if key should be parsed as int and has value, otherwise according to :func:`parse_str`.
        """
        convert = False
        if value:
            if key in cls._parse_as_int:
                convert = True
            else:
                for item in cls._parse_as_int_suffix:
                    if key.endswith(item):
                        convert = True
        return int(value) if convert and value.isnumeric() else parse_str(value)


@dataclass
class Git(git.Repo):
    """
    Dataclass Wrapper for :class:`git.Repo`.

    Represents a git repository and allows you to query references,
    gather commit information, generate diffs, create and clone repositories query
    the log.

    'working_tree_dir' is the working tree directory, but will raise AssertionError if we are a bare repository.
    """
    git: GitCmd = field(init=False)
    """
    The Git class manages communication with the Git binary.
    
    It provides a convenient interface to calling the Git binary, such as in::

     g = Git( git_dir )
     g.init()                   # calls 'git init' program
     rval = g.ls_files()        # calls 'git ls-files' program

    ``Debugging``
        Set the GIT_PYTHON_TRACE environment variable print each invocation
        of the command to stdout.
        Set its value to 'full' to see details about the returned values.

    """
    git_dir: AnyPath | None = field(default=None, init=False)
    """the .git repository directory, which is always set"""
    odb: Type[LooseObjectDB] = field(init=False)
    working_dir: AnyPath | None = field(default=None, init=False)
    """working directory of the git command, which is the working tree
    directory if available or the .git directory in case of bare repositories"""

    path: InitVar[AnyPath | None] = None
    """File or Directory inside the git repository, the default with search_parent_directories"""
    expand_vars: InitVar[bool] = True
    odbt: InitVar[Type[LooseObjectDB]] = GitCmdObjectDB
    """the path to either the root git directory or the bare git repo"""
    search_parent_directories: InitVar[bool] = True
    """if True, all parent directories will be searched for a valid repo as well."""
    def __post_init__(self, path: AnyPath | None, expand_vars: bool,
                      odbt: Type[LooseObjectDB], search_parent_directories: bool):
        """
        Create a new Repo instance

        Examples:
            >>> assert Git(__file__)
            >>> Git("~/repo.git")  # doctest: +SKIP
            >>> Git("${HOME}/repo")  # doctest: +SKIP

        Raises:
            InvalidGitRepositoryError
            NoSuchPathError

        Args:
            path: File or Directory inside the git repository, the default with search_parent_directories set to True
                or the path to either the root git directory or the bare git repo
                if search_parent_directories is changed to False
            expand_vars: if True, environment variables will be expanded in the given path
            search_parent_directories: Search all parent directories for a git repository.
        Returns:
            Git: Git instance
        """
        super(Git, self).__init__(path if path is None else Path(path).directory(), expand_vars=expand_vars,
                                  odbt=odbt, search_parent_directories=search_parent_directories)

    @property
    def top(self) -> Path:
        """Git Top Directory Path."""
        path = Path(self.working_dir)
        return Path(path.parent if ".git" in path else path)

@dataclass
class Releaser(git.Repo):
    """The :class:`git.Repo` object."""
    path: Path = field(default_factory=Path)
    git: Git = field(default_factory=Git, init=False)


class TempDir(tempfile.TemporaryDirectory):
    """
    Wrapper for :class:`tempfile.TemporaryDirectory` that provides Path-like
    """
    def __enter__(self) -> Path:
        """
        Return the path of the temporary directory

        Returns:
            Path of the temporary directory
        """
        return Path(self.name)


async def aiocmd(*args, **kwargs) -> CompletedProcess:
    """
    Async Exec Command

    Examples:
        >>> with TempDir() as tmp:
        ...     rv = asyncio.run(aiocmd("git", "clone", "https://github.com/octocat/Hello-World.git", cwd=tmp))
        ...     assert rv.returncode == 0
        ...     assert (tmp / "Hello-World" / "README").exists()

    Args:
        *args: command and args
        **kwargs: subprocess.run kwargs

    Raises:
        JetBrainsError

    Returns:
        None
    """
    proc = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE, **kwargs)

    stdout, stderr = await proc.communicate()
    completed = subprocess.CompletedProcess(args, returncode=proc.returncode,
                                            stdout=stdout.decode() if stdout else None,
                                            stderr=stderr.decode() if stderr else None)
    if completed.returncode != 0:
        raise CmdError(completed)
    return completed


cli_invoke = CliRunner().invoke


def cmd(*args, **kwargs) -> CompletedProcess:
    """
    Exec Command

    Examples:
        >>> with TempDir() as tmp:
        ...     rv = cmd("git", "clone", "https://github.com/octocat/Hello-World.git", tmp)
        ...     assert rv.returncode == 0
        ...     assert (tmp / "README.md").exists()

    Args:
        *args: command and args
        **kwargs: subprocess.run kwargs

    Raises:
        CmdError

    Returns:
        None
    """

    completed = subprocess.run(args, **kwargs, capture_output=True, text=True)

    if completed.returncode != 0:
        raise CmdError(completed)
    return completed


def parse_env(name: str = "USER") -> bool | Path | ParseResult | IPv4Address | IPv6Address | int | str | None:
    """
    Parses variable from environment using :func:`mreleaser.parse_str`,
    except ``SUDO_UID`` or ``SUDO_GID`` which are parsed as int instead of bool.

    Arguments:
        name: variable name to parse from environment (default: USER)

    Examples:
        >>> assert isinstance(parse_env(), str)
        >>>
        >>> os.environ['FOO'] = '1'
        >>> assert parse_env("FOO") is True
        >>>
        >>> os.environ['FOO'] = '0'
        >>> assert parse_env("FOO") is False
        >>>
        >>> os.environ['FOO'] = 'TrUe'
        >>> assert parse_env("FOO") is True
        >>>
        >>> os.environ['FOO'] = 'OFF'
        >>> assert parse_env("FOO") is False
        >>>
        >>> os.environ['FOO'] = '~/foo'
        >>> assert parse_env("FOO") == Path('~/foo')
        >>>
        >>> os.environ['FOO'] = '/foo'
        >>> assert parse_env("FOO") == Path('/foo')
        >>>
        >>> os.environ['FOO'] = './foo'
        >>> assert parse_env("FOO") == Path('./foo')
        >>>
        >>> os.environ['FOO'] = './foo'
        >>> assert parse_env("FOO") == Path('./foo')
        >>>
        >>> v = "https://github.com"
        >>> os.environ['FOO'] = v
        >>> assert parse_env("FOO").geturl() == v
        >>>
        >>> v = "git@github.com"
        >>> os.environ['FOO'] = v
        >>> assert parse_env("FOO").geturl() == v
        >>>
        >>> v = "0.0.0.0"
        >>> os.environ['FOO'] = v
        >>> assert parse_env("FOO").exploded == v
        >>>
        >>> os.environ['FOO'] = "::1"
        >>> assert parse_env("FOO").exploded.endswith(":0001")
        >>>
        >>> v = "2"
        >>> os.environ['FOO'] = v
        >>> assert parse_env("FOO") == int(v)
        >>>
        >>> v = "2.0"
        >>> os.environ['FOO'] = v
        >>> assert parse_env("FOO") == v
        >>>
        >>> del os.environ['FOO']
        >>> assert parse_env("FOO") is None
        >>>
        >>> assert isinstance(parse_env("PATH"), str)

    Returns:
        None
    """
    if value := os.environ.get(name):
        return Env.as_int(name, value)
    return value


def parse_str(data: Any | None = None) -> bool | Path | ParseResult | IPv4Address | IPv6Address | int | str | None:
    """
    Parses str or data.__str__()

    Parses:
        - bool: 1, 0, True, False, yes, no, on, off (case insensitive)
        - int: integer only numeric characters but 1 and 0
        - ipaddress: ipv4/ipv6 address
        - url: if "://" or "@" is found it will be parsed as url
        - path: if "." or start with "/" or "~" or "." and does contain ":"
        - others as string

    Arguments:
        data: variable name to parse from environment (default: USER)

    Examples:
        >>> assert parse_str() is None
        >>>
        >>> assert parse_str("1") is True
        >>> assert parse_str("0") is False
        >>> assert parse_env("TrUe") is True
        >>> assert parse_str("OFF") is False
        >>>
        >>> assert parse_str("https://github.com").geturl() == "https://github.com"
        >>> assert parse_str("git@github.com").geturl() == "git@github.com"
        >>>
        >>> assert parse_str("~/foo") == Path('~/foo')
        >>> assert parse_str("/foo") == Path('/foo')
        >>> assert parse_str("./foo") == Path('./foo')
        >>> assert parse_str(".") == Path('./foo')
        >>> assert parse_str(Path()) == Path()
        >>> assert isinstance(parse_str(Git()), Path)
        >>>
        >>> assert parse_str("0.0.0.0").exploded == "0.0.0.0"
        >>> assert parse_str("::1").exploded.endswith(":0001")
        >>>
        >>> assert parse_str("2") == 2
        >>> assert parse_str("2.0") == "2.0"
        >>> assert parse_str("/usr/share/man:") == "/usr/share/man:"
        >>> assert isinstance(parse_str(os.environ["PATH"]), str)

    Returns:
        None
    """
    if data is not None:
        if not isinstance(data, str): data = str(data)

        if data.lower() in ['1', 'true', 'yes', 'on']:
            return True
        elif data.lower() in ['0', 'false', 'no', 'off']:
            return False
        elif '://' in data or '@' in data:
            return urllib.parse.urlparse(data)
        elif (data[0] in ['/', '~', './'] and ":" not in data) or data == ".":
            return Path(data)
        else:
            try:
                return ipaddress.ip_address(data)
            except ValueError:
                if data.isnumeric():
                    return int(data)
    return data


def suppress(func: Callable[P, T], *args: P.args, exception: ExcType | None = Exception, **kwargs: P.kwargs) -> T:
    """
    Try and supress exception.

    Args:
        func: function to call
        *args: args to pass to func
        exception: exception to suppress (default: Exception)
        **kwargs: kwargs to pass to func

    Returns:
        result of func
    """
    with contextlib.suppress(exception or Exception):
        return func(*args, **kwargs)


def version(package: str = __project__) -> str:
    """
    Package installed version

    Examples:
        >>> from semver import VersionInfo
        >>> assert VersionInfo.parse(version("pip"))

    Arguments:
        package: package name (Default: `PROJECT`)

    Returns
        Installed version
    """
    return suppress(importlib.metadata.version, package or Path(__file__).parent.name,
                    exception=importlib.metadata.PackageNotFoundError)


@app.command(name="package")
def _package(path: Optional[list[Path]] = Argument('.', help='Directory Path to package'),) -> None:
    """
    Prints the package name from setup.cfg in path.

    \b


    Returns:
        None
    """
    print(version())


@app.command(name="--version")
def _version() -> None:
    """
    Prints the installed version of the package.

    Returns:
        None
    """
    print(version())


if __name__ == "__main__":
    from typer import Exit
    try:
        Exit(app())
    except KeyboardInterrupt:
        print('Aborted!')
        Exit()
