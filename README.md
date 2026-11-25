# Remote 3 Integration Lab

Development workspace for Unfolded Circle Remote 3 integrations. The Dock 3 is part of the hardware setup, not a second integration runtime. No device-specific integration ships in this scaffold. The intended deployment is on Remote 3 itself; external execution is the development path and a fallback, not a required appliance. This is an independent project, not affiliated with or endorsed by Unfolded Circle.

## License

Original project material is licensed under the [Mozilla Public License 2.0](LICENSE), unless stated otherwise. Other components keep their original terms. Product names identify compatibility targets, not affiliation.

## Start here

- [Research and first decisions](docs/research.md)
- [Development and validation playbook](docs/development.md)
- [Local release packaging and safety gates](docs/release.md)
- [Adding an integration](integrations/README.md)
- [Agent guide](AGENTS.md)

```sh
make check
```

The repo tools use only Python 3.11+ and Make. Checks operate on synthetic fixtures, never the LAN or your hardware. Override the interpreter with `make PYTHON=python3.11 check`. CI performs the same checks, with no hardware credentials, artifact publication, or release trigger. A future driver should pin its own SDK and runtime dependencies separately.
