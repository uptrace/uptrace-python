from nox import session


@session(python=["3.8", "3.9", "3.10"], reuse_venv=True)
def test(session):
    session.install(".")
    session.install("-r", "dev-requirements.txt")
    session.run("pytest", external=True)


@session(python=["3.10"], reuse_venv=True)
def lint(session):
    session.install(".")
    session.install("-r", "dev-requirements.txt")
    session.run("black", "src")
    session.run("isort", "src")
    session.run("pylint", "src/uptrace")
