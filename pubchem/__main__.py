import argparse
import logging
import pathlib
from os.path import expanduser

from .pc_commands import find, pull


def elastic_args_inject(parser) -> None:
    parser.add_argument(
        "--elastic-url",
        type=str,
        help="Elastic URL in RFC-1738 format https://user:password@host:port",
        default="https://admin:admin@localhost:9200",
    )
    parser.add_argument(
        "--elastic-verify-certs",
        default=False,
        action="store_true",
        help="Force client to verify ssl certs",
    )
    parser.add_argument(
        "--elastic-no-verify-certs",
        action="store_false",
        dest="elastic-verify-certs",
        help="Don't verify certs",
    )
    parser.add_argument(
        "--elastic-index",
        type=str,
        help="Name of the index in Elastic",
        default="pubchem",
    )


def pull_args_inject(parser) -> None:
    parser_pull = parser.add_parser("pull")
    parser_pull.add_argument(
        "--workdir", default=pathlib.Path(expanduser("~")) / "pubchem"
    )
    parser_pull.add_argument(
        "--tmpdir", default=pathlib.Path(expanduser("~")) / "pubchem" / "tmp"
    )
    elastic_args_inject(parser_pull)
    parser_pull.set_defaults(func=pull)


def find_args_inject(parser) -> None:
    parser_find = parser.add_parser("find")
    parser_find.add_argument(
        "--canonical-smiles",
        help="search molecule represented by canonical smiles",
        type=str,
    )
    parser_find.add_argument(
        "--exact-match", action="store_true", help="search exact match"
    )
    parser_find.add_argument(
        "--sim-search",
        help="similarity search",
        choices=("tanimoto", "tversky"),
    )
    elastic_args_inject(parser_find)
    parser_find.set_defaults(func=find)


def init_logger():
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=logging.WARNING,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


if __name__ == "__main__":

    init_logger()

    parser = argparse.ArgumentParser(description="Pubchem crawler")
    subparsers = parser.add_subparsers(help="select mode")
    pull_args_inject(subparsers)
    find_args_inject(subparsers)

    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        parser.print_help()
