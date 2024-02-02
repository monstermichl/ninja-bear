from __future__ import annotations
import os
import re
import tempfile

from ..helpers.shell import execute_commands
from ..base.info import VERSION
from ..base.distributor_base import DistributorBase


class GitVersion:
    major: str
    minor: str
    patch: str

    def __init__(self, major, minor, patch) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch

    @staticmethod
    def from_git() -> GitVersion:
        code, text, _ = execute_commands('git --version')
        version_text = text if code == 0 else ''

        return GitVersion.from_string(version_text)  # TODO: Throw exception if there is a problem with git.

    @staticmethod
    def from_string(version_string: str) -> GitVersion:
        version = GitVersion(0, 0, 0)
        match = re.search('\d+\.\d+\.\d+', version_string)

        if match:
            parts = match.group(0).split('.')

            version.major = int(parts[0])
            version.minor = int(parts[1])
            version.patch = int(parts[2])
        return version


class GitDistributor(DistributorBase):
    _MIN_GIT_VERSION = GitVersion(2, 29, 0)  # Needs at least git version 2.29.0 as it introduced partial-clone (https://www.git-scm.com/docs/partial-clone).

    def __init__(self, url: str, target_path: str, user: str, password: str):
        super().__init__()

        self._url = url
        self._target_path = target_path if target_path else ''  # Use root directory as default path.

    def distribute(self, file_name: str, data: str) -> DistributorBase:
        version = GitVersion.from_git()
        
        if version.major < self._MIN_GIT_VERSION.major or \
           version.minor < self._MIN_GIT_VERSION.minor or \
           version.patch < self._MIN_GIT_VERSION.patch:
            pass  # TODO: Throw exception.
        else:
            # Create temporary folder to clone the git repo into and work with it.
            with tempfile.TemporaryDirectory() as temp_dir:

                # Only clone desired target folder.
                code, _, _ = execute_commands(*[
                    f'git clone --filter=blob:none --no-checkout {self._url} {temp_dir}',
                    f'pushd {temp_dir}',
                    f'git sparse-checkout set {self._target_path}' if self._target_path else '',
                    'git checkout',
                ])

                # If checkout was successful, go on.
                if code == 0:
                    # Make sure target directory exists.
                    if self._target_path:
                        os.makedirs(os.path.join(temp_dir, self._target_path), exist_ok=True)

                    target_file_path = os.path.join(self._target_path, file_name)
                    target_file_path_full = os.path.join(temp_dir, target_file_path)

                    # Write data to target file.
                    with open(target_file_path_full, 'w') as f:
                        f.write(data)

                    # Commit and push changes to repo.
                    code, _, _ = execute_commands(*[
                        f'pushd {temp_dir}',
                        f'git add "{target_file_path}"',
                        f'git commit "{target_file_path}" -m "Update {target_file_path} via confluent v{VERSION}"',
                        'git push',
                    ])
        return self
