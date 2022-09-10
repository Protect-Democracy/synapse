# Contributing

There are multiple ways to contribute to this project. As always, you must adhere to this project's [Code of Conduct](./CODE_OF_CONDUCT.md).

## Bug reports, feature requests, and other issues

If you are having a problem with this project, adding an issue in the Issue Queue will be very helpful. Make sure to give as much information as possible to ensure that the issue can be addressed.

## Documentation contributions

See [docs/DOCUMENTATION.md](./DOCUMENTATION.md).

## Code contributions

To contribute code to this project, the general process is the following:

- (optional) Fork this project if you don't have access to push to this repo directly.
- Make a branch that starts with `feature/`, `bugfix/`, or `maintenance/`.
- Do your development.
- Push your branch and make a Pull Request.

### Developing

#### Setup

The following is how you setup your development environment to work on this project:

- Install Poetry
- Install dependencies: `poetry install`
- Use Poetry environment: `poetry shell`

#### Updates

When pulling new code, you should do the following:

- To update any dependencies run: `poetry install`

#### Code styles and linting

See [docs/CODING_STYLES_LINTING.md](./CODING_STYLES_LINTING.md).

#### Writing tests

When writing code, you will likely want to write some tests:

- Tests are in the `tests/` directory and are run with [pytest](https://docs.pytest.org/).

### Running tests

To run tests, you should do the following:

```bash
poetry run pytest
```

### Email template

Email design on [stripo.email](https://my.stripo.email/cabinet/#/template-editor/?projectId=684149&templateId=1544434&type=MY_TEMPLATE&templateProjectId=470969).
