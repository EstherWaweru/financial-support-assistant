from abc import ABCMeta, abstractmethod

from typing import Any, AnyStr, Dict, List, Optional, Tuple, Union
from collections import defaultdict

from sqlalchemy.sql.elements import or_
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.schema import Column
from inflection import underscore

"""
All ransacker query commands inherit from Command.
They are named after the actual suffix command name in CamelCase and
automatically added into the available command list.

https://github.com/activerecord-hackery/ransack#search-matchers

Examples:   - Gt    -> _gt
            - Lteq  -> _lteq
            - NotEq -> _not_eq
"""


class Command:
    __metaclass__ = ABCMeta

    @abstractmethod
    def apply_command(
        self, value: Union[AnyStr, List[AnyStr]], column: Column, query: Query
    ) -> Query:
        raise NotImplementedError  # pragma: no cover

    def __str__(self) -> str:
        return self.__class__.__name__

    def __eq__(self, other: object) -> bool:
        return self.__str__() == other.__str__()

    def __hash__(self) -> int:
        return self.__str__().__hash__()


class Eq(Command):
    def apply_command(
        self,
        value: Union[AnyStr, List[AnyStr], Dict[str, str]],
        column: Column,
        query: Query,
    ) -> Query:
        if isinstance(value, dict):
            return query.filter(column.between(value["start"], value["end"]))
        else:
            return query.filter(column == value)


class NotEq(Command):
    def apply_command(
        self, value: Union[AnyStr, List[AnyStr]], column: Column, query: Query
    ) -> Query:
        return query.filter(column != value)


class Gt(Command):
    def apply_command(
        self, value: Union[AnyStr, List[AnyStr]], column: Column, query: Query
    ) -> Query:
        return query.filter(column > value)


class Gteq(Command):
    def apply_command(
        self, value: Union[AnyStr, List[AnyStr]], column: Column, query: Query
    ) -> Query:
        return query.filter(column >= value)


class Lt(Command):
    def apply_command(
        self, value: Union[AnyStr, List[AnyStr]], column: Column, query: Query
    ) -> Query:
        return query.filter(column < value)


class Lteq(Command):
    def apply_command(
        self, value: Union[AnyStr, List[AnyStr]], column: Column, query: Query
    ) -> Query:
        return query.filter(column <= value)


class In(Command):
    def apply_command(
        self, value: Union[AnyStr, List[AnyStr]], column: Column, query: Query
    ) -> Query:
        return query.filter(column.in_(value))


class NotIn(Command):
    def apply_command(
        self, value: Union[AnyStr, List[AnyStr]], column: Column, query: Query
    ) -> Query:
        return query.filter(~(column.in_(value)))


class Null(Command):
    def apply_command(
        self, value: Union[AnyStr, List[AnyStr]], column: Column, query: Query
    ) -> Query:
        return query.filter(column == None)  # noqa: E711


class NotNull(Command):
    def apply_command(
        self, value: Union[AnyStr, List[AnyStr]], column: Column, query: Query
    ) -> Query:
        return query.filter(column != None)  # noqa: E711


class Blank(Command):
    def apply_command(
        self, value: Union[AnyStr, List[AnyStr]], column: Column, query: Query
    ) -> Query:
        return query.filter(or_(column == None, column == ""))  # noqa: E711


class Filter:
    commands: Dict[str, Command] = {}

    # add all available commands to the list
    # we sort the list by the length of the command in reversed order, so we don't
    # match commands that are part of other commands before the correct command
    # for example: _not_eq and _eq
    for command in sorted(
        Command.__subclasses__(), key=lambda e: len(e.__name__), reverse=True
    ):
        commands[f"_{underscore(command.__name__)}"] = command()  # type: ignore

    def get_command(self, query: str) -> Optional[Tuple[str, Command]]:
        match = next((cmd for cmd in self.commands.keys() if query.endswith(cmd)), "")
        if match != "":
            return (query.removesuffix(match), self.commands[match])

        return None

    filter_list: Dict[str, Dict[Command, Union[str, List[str]]]]

    def __init__(self) -> None:
        self.filter_list = defaultdict(lambda: {})

    def add_command(
        self, key: str, command: Command, value: Any, array: bool = False
    ) -> None:
        if key in self.filter_list.keys():
            item = self.filter_list[key]
            if command in item.keys() and array and isinstance(item[command], list):
                item[command].append(value)  # type: ignore
                self.filter_list[key][command] = item[command]
                return
        if array:
            self.filter_list[key][command] = [value]
        else:
            self.filter_list[key][command] = value


description = f"""
    Endpoint supports generic ransacker style queries or direct attribute queries.

    https://github.com/activerecord-hackery/ransack#search-matchers

    Supported ransacker commands right now: {", ".join(Filter.commands.keys())}.

    Examples 1: endpoint/?q[some_attribute_gt]=20000
    Examples 3: endpoint/?q[some_attribute_in][]=a&q[some_attribute_in][]=b
    Examples 2: endpoint/?some_attribute_id=1
"""
