"""Classes and types for handling and representing FHIR Interactions."""

from abc import abstractmethod
from collections.abc import Callable, Coroutine, Mapping
from dataclasses import dataclass
from typing import Any, Generic, Literal, TypeVar

from fastapi import Request, Response

from .resources import Bundle, Id, Resource, OperationOutcome

ResourceType = TypeVar("ResourceType", bound=Resource)


@dataclass
class InteractionContext:
    request: Request
    response: Response


CreateInteractionHandler = Callable[
    [InteractionContext, ResourceType],
    Coroutine[None, None, Id | ResourceType] | Id | ResourceType,
]
ReadInteractionHandler = Callable[
    [InteractionContext, Id], Coroutine[None, None, ResourceType] | ResourceType
]
VReadInteractionHandler = Callable[
    [InteractionContext, Id, Id], Coroutine[None, None, ResourceType] | ResourceType
]
SearchTypeInteractionHandler = Callable[..., Coroutine[None, None, Bundle] | Bundle]
HistoryInteractionHandler = Callable[
    [InteractionContext, Id], Coroutine[None, None, Bundle] | Bundle
]
UpdateInteractionHandler = Callable[
    [InteractionContext, Id, ResourceType],
    Coroutine[None, None, Id | ResourceType] | Id | ResourceType,
]
PatchInteractionHandler = Callable[
    [InteractionContext, Id, dict | str],
    Coroutine[None, None, Id | ResourceType] | Id | ResourceType,
]
DeleteInteractionHandler = Callable[
    [InteractionContext, Id],
    Coroutine[None, None, OperationOutcome | None] | OperationOutcome | None,
]


InteractionHandler = (
    CreateInteractionHandler[ResourceType]
    | ReadInteractionHandler[ResourceType]
    | VReadInteractionHandler[ResourceType]
    | SearchTypeInteractionHandler
    | HistoryInteractionHandler
    | UpdateInteractionHandler[ResourceType]
    | PatchInteractionHandler[ResourceType]
    | DeleteInteractionHandler
)


class TypeInteraction(Generic[ResourceType]):
    """
    Collection of values that represent a FHIR type interactions. This class can also represent
    instance level interactions.

    resource_type:    The type of FHIR resource on which this interaction operates, as defined by
                      the fhir.resources package.
    handler:          User-defined function that performs the FHIR interaction.
    route_options:    Dictionary of key-value pairs that are passed on to FastAPI on route creation.
    """

    def __init__(
        self,
        resource_type: type[ResourceType],
        handler: InteractionHandler[ResourceType],
        route_options: Mapping[str, Any],
    ):
        self.resource_type = resource_type
        self.handler = handler
        self.route_options = route_options

    @staticmethod
    @abstractmethod
    def label() -> str:
        raise NotImplementedError


class CreateInteraction(TypeInteraction[ResourceType]):
    @staticmethod
    def label() -> Literal["create"]:
        return "create"


class ReadInteraction(TypeInteraction[ResourceType]):
    @staticmethod
    def label() -> Literal["read"]:
        return "read"


class VReadInteraction(TypeInteraction[ResourceType]):
    @staticmethod
    def label() -> Literal["vread"]:
        return "vread"


class SearchTypeInteraction(TypeInteraction[ResourceType]):
    @staticmethod
    def label() -> Literal["search-type"]:
        return "search-type"


class HistoryInteraction(TypeInteraction[ResourceType]):
    @staticmethod
    def label() -> Literal["history"]:
        return "history"


class UpdateInteraction(TypeInteraction[ResourceType]):
    @staticmethod
    def label() -> Literal["update"]:
        return "update"


class PatchInteraction(TypeInteraction[ResourceType]):
    @staticmethod
    def label() -> Literal["patch"]:
        return "patch"


class DeleteInteraction(TypeInteraction[ResourceType]):
    @staticmethod
    def label() -> Literal["delete"]:
        return "delete"
