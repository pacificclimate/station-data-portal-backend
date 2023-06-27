# Development caveats

## Poetry and the PCIC PyPI server

The current version of Poetry (1.4.x) only uses SHA256 hashes for checking 
the validity of packages. (This actually goes back to a much earlier version 
of Poetry, so installing an older version of Poetry isn't a desirable option.)

At present, our PyPI server only provides MD5 hashes.

This, naturally, causes a problem for 
developers when they update the `poetry.lock` file, which happens whenever
dependencies are changed.

There are two possible solutions:

1. [Manually add MD5 hash entries for offending packages to `poetry.lock` after it fails to install.](https://github.com/python-poetry/poetry/issues/6301#issuecomment-1238770092) Do this every time you re-lock the installation. This works, but it will get tedious fairly quickly.
2. [Make our PyPI server use SHA 256 hashes.](https://github.com/python-poetry/poetry/issues/6301#issuecomment-1348588218) Risks: If other installation managers we use require MD5 hashes. Are there such?

At present, we use solution 1 above -- manually add the hash. The error message from Poetry tells you the hash to add, which is convenient. Check the existing `poetry.lock`, package `pycds` for an example of the MD5 hash addition. Note: It will be removed by Poetry whenever you re-lock the project. Check the original version of `poetry.lock`.
