# Summary
This project is meant to automate signing into your southwest flight. It was created by examining the HTTP requests that the [mobile site](https://mobile.southwest.com/check-in) makes to check into your flight. The main source that does this can be found in [`southwest_api.py`](https://github.com/matthewgrossman/southwest/blob/master/southwest_api.py).

There is another file [`southwest.py`](https://github.com/matthewgrossman/southwest/blob/master/southwest.py#L12) that attempts to sign in by interacting with a browser. That code isn't currently functional, though you feel free to browse it to see some [`selenium`](https://selenium-python.readthedocs.io/) usages.

# Usage
1. Download and install dependencies
    ```shell
    $ git clone https://github.com/matthewgrossman/southwest.git
    $ cd southwest
    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt
    ```
1. Run script

    Example usage:
    ```shell
    $ python cli.py -a schedule --confirmation-num TRKUW6 --first-name Matthew --last-name Grossman
    ```

    Help docs:
    ```shell
    Usage: cli.py [OPTIONS]

    Options:
    -c, --confirmation-num TEXT     flight confirmation number (e.g. LFKWNT)
                                    [required]
    -f, --first-name TEXT           first name (e.g. John)  [required]
    -l, --last-name TEXT            last name (e.g. Smith)  [required]
    -a, --action [schedule|checkin]
                                    [required]
    --help                          Show this message and exit.
    ```
