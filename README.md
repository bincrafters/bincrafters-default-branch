[![Build Status](https://travis-ci.com/bincrafters/bincrafters-default-branch.svg?branch=master)](https://travis-ci.com/bincrafters/bincrafters-default-branch)

# Bincrafters Default Branch

#### A Script to update Github default branch

#### About

This script was created with the intention to update all Bincrafters projects to use the
latest **testing** branch available in each project.

#### Running

    pip install -r requirement.txt
    export GITHUB_USERNAME=<your github username>
    export GITHUB_API_KEY=<Github Personal access tokens>
    export GITHUB_API_KEY=<Github Personal access tokens>
    export GITHUB_ORGANIZATION=<Organization to be updated>
    python bincrafters_default_branch.py
    
#### How to obtain an access token?

Visit https://github.com/settings/tokens and generate a personal token.

#### License
[MIT](LICENSE)
