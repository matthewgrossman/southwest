import click
from southwest import Southwest


class Actions:
    SCHEDULE = 'schedule'
    CHECK_IN = 'check-in'


@click.command()
@click.option('-a', '--action', required=True, type=click.Choice([Actions.SCHEDULE, Actions.CHECK_IN]))
@click.option('-c', '--confirmation-num', required=True, help='flight confirmation number (e.g. LFKWNT)')
@click.option('-f', '--first-name', required=True, help='first name (e.g. John)')
@click.option('-l', '--last-name', required=True, help='last name (e.g. Smith)')
def cli(action: str, confirmation_num: str, first_name: str, last_name: str) -> None:
    southwest = Southwest(confirmation_num=confirmation_num, first_name=first_name, last_name=last_name)
    if action == Actions.CHECK_IN:
        southwest.check_in()
    else:
        southwest.schedule()


if __name__ == '__main__':
    cli()
