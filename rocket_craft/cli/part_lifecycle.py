import click
import shutil

from typing import Any
import yaml

from craft_parts import LifecycleManager, Step

from plugins import register_plugins


def _run(stage: Step, parts_file: str, work_dir: str, cache_dir: str):
    register_plugins()

    parts: dict[str, Any]

    with open(parts_file, "r") as f:
        parts = yaml.safe_load(f)

    lcm = LifecycleManager(
        parts, application_name="rocketcraft", cache_dir=cache_dir, work_dir=work_dir
    )

    step: Step
    if stage == "pull":
        step = Step.PULL
    elif stage == "build":
        step = Step.BUILD
    elif stage == "stage":
        step = Step.STAGE
    elif stage == "prime":
        step = Step.PRIME
    else:
        raise click.ClickException(f"Invalid stage: {stage}")

    actions = lcm.plan(step)

    with lcm.action_executor() as aex:
        aex.execute(actions)


@click.command()
@click.argument("stage", type=click.Choice(["pull", "build", "stage", "prime"]))
@click.option("--parts-file", type=click.Path(exists=True), default="parts.yaml")
@click.option("--work-dir", type=click.Path(), default="./work")
@click.option("--cache-dir", type=click.Path(), default="./cache")
@click.option("--force-rerun", is_flag=True, default=False)
def parts(
    stage: str, parts_file: str, work_dir: str, cache_dir: str, force_rerun: bool
):
    if force_rerun:
        shutil.rmtree(work_dir, ignore_errors=True)
        shutil.rmtree(cache_dir, ignore_errors=True)
    _run(stage, parts_file, work_dir, cache_dir)
