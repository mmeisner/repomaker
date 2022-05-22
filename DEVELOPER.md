# repomaker DEVELOPER Notes

Notes for myself (and other developers)


## Packaging

Build package with:

```shell
python3 -m pip install --upgrade build
python3 -m build
```

Afterwards, install package and list its contents with:

```shell
pip install --force-reinstall dist/repomaker-*-py3-none-any.whl
pip show -f repomaker
```

## Resources

See [Packaging Python Projects — Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)