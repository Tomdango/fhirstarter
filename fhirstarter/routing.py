from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
import re
from abc import abstractstaticmethod, ABC
from .fhir_specification.utils import is_resource_type
from fastapi import Request

_METADATA_PATH_REGEX = re.compile(r".*?/metadata")
_READ_PATH_REGEX = re.compile(
    r".*?/(?P<resource_type>[A-z]*)/(?P<resource_id>[A-Za-z0-9\-\.]{1,64})$"
)
_VREAD_PATH_REGEX = re.compile(
    r".*?/(?P<resource_type>[A-z]*)/(?P<resource_id>[A-Za-z0-9\-\.]{1,64})/_history/(?P<version_id>[A-Za-z0-9\-\.]{1,64})$"
)
_CREATE_PATH_REGEX = re.compile(r".*?/(?P<resource_type>[A-z]*)$")
_SEARCH_TYPE_GET_PATH_REGEX = re.compile(r".*?/(?P<resource_type>[A-z]*)$")
_SEARCH_TYPE_POST_PATH_REGEX = re.compile(r".*?/(?P<resource_type>[A-z]*)/_search$")
_UPDATE_PATH_REGEX = re.compile(
    r".*?/(?P<resource_type>[A-z]*)/(?P<resource_id>[A-Za-z0-9\-\.]{1,64})$"
)
_PATCH_PATH_REGEX = re.compile(
    r".*?/(?P<resource_type>[A-z]*)/(?P<resource_id>[A-Za-z0-9\-\.]{1,64})$"
)
_DELETE_PATH_REGEX = re.compile(
    r".*?/(?P<resource_type>[A-z]*)/(?P<resource_id>[A-Za-z0-9\-\.]{1,64})$"
)


InteractionType = Literal[
    "create",
    "read",
    "vread",
    "update",
    "search-type",
    "delete",
    "capabilities",
    "patch",
]


@dataclass
class InteractionInfo:
    resource_type: str | None
    interaction_type: InteractionType | None
    resource_id: str | None
    version_id: str | None

    @staticmethod
    def empty() -> InteractionInfo:
        return InteractionInfo(
            resource_type=None,
            interaction_type=None,
            resource_id=None,
            version_id=None,
        )

    @staticmethod
    def from_match(
        match: re.Match[str] | None, interaction_type: InteractionType
    ) -> InteractionInfo | None:
        """
        Create InteractionInfo object from regex match and interaction type
        Ensures that the resource type is a valid FHIR resource type
        Returns None if the match or resource type is not valid
        """
        if not match:
            return None

        match_data = match.groupdict()
        resource_type = match_data.get("resource_type")

        if not resource_type or not is_resource_type(resource_type):
            return None

        return InteractionInfo(
            resource_type=resource_type,
            interaction_type=interaction_type,
            resource_id=match_data.get("resource_id"),
            version_id=match_data.get("version_id"),
        )


class PathMatcher(ABC):
    """Base Path Matcher Resource"""

    @staticmethod
    @abstractstaticmethod
    def match(_method: str, _path: str) -> InteractionInfo | None:
        """
        To be implemented by child classes
        If the method and path matches the matcher, return an InteractionInfo object
        Otherwise, return None
        """
        raise NotImplementedError


class MetadataPathMatcher(PathMatcher):
    """Path Matcher for the metadata interaction"""

    @staticmethod
    def match(method: str, path: str) -> InteractionInfo | None:
        """Check if the path matches the metadata path"""
        if method != "GET":
            return None

        if not _METADATA_PATH_REGEX.match(path):
            return None

        return InteractionInfo(
            resource_type=None,
            interaction_type="capabilities",
            resource_id=None,
            version_id=None,
        )


class CreatePathMatcher(PathMatcher):
    """Path Matcher for the create interaction"""

    @staticmethod
    def match(method: str, path: str) -> InteractionInfo | None:
        if method != "POST":
            return None

        match = _CREATE_PATH_REGEX.match(path)
        return InteractionInfo.from_match(match, "create")


class ReadPathMatcher(PathMatcher):
    """Path Matcher for the read interaction"""

    @staticmethod
    def match(method: str, path: str) -> InteractionInfo | None:
        """Check if the path matches the read interaction path"""
        if method != "GET":
            return None

        match = _READ_PATH_REGEX.match(path)
        return InteractionInfo.from_match(match, "read")


class VReadPathMatcher(PathMatcher):
    """Path Matcher for the vread interaction"""

    @staticmethod
    def match(method: str, path: str) -> InteractionInfo | None:
        """Check if the path matches the vread interaction path"""
        if method != "GET":
            return None

        match = _VREAD_PATH_REGEX.match(path)
        return InteractionInfo.from_match(match, "vread")


class SearchPathMatcher(PathMatcher):
    """Path Matcher for the search interaction"""

    @staticmethod
    def match(method: str, path: str) -> InteractionInfo | None:
        """Check if the path matches the search interaction path"""
        if method not in ["GET", "POST"]:
            return None

        if method == "GET":
            match = _SEARCH_TYPE_GET_PATH_REGEX.match(path)
            return InteractionInfo.from_match(match, "search-type")

        assert method == "POST", "Method should be POST"

        match = _SEARCH_TYPE_POST_PATH_REGEX.match(path)
        return InteractionInfo.from_match(match, "search-type")


class UpdatePathMatcher(PathMatcher):
    """Path Matcher for the update interaction"""

    @staticmethod
    def match(method: str, path: str) -> InteractionInfo | None:
        """Check if the path matches the update interaction path"""
        if method != "PUT":
            return None

        match = _UPDATE_PATH_REGEX.match(path)
        return InteractionInfo.from_match(match, "update")


class PatchPathMatcher(PathMatcher):
    """Path Matcher for the patch interaction"""

    @staticmethod
    def match(method: str, path: str) -> InteractionInfo | None:
        """Check if the path matches the patch interaction path"""
        if method != "PATCH":
            return None

        match = _PATCH_PATH_REGEX.match(path)
        return InteractionInfo.from_match(match, "patch")


class DeletePathMatcher(PathMatcher):
    """Path Matcher for the delete interaction"""

    @staticmethod
    def match(method: str, path: str) -> InteractionInfo | None:
        """Check if the path matches the patch interaction path"""
        if method != "DELETE":
            return None

        match = _DELETE_PATH_REGEX.match(path)
        return InteractionInfo.from_match(match, "delete")


def parse_fhir_request(request: Request | None) -> InteractionInfo:
    """
    Parses the request into a InteractionInfo object
    """
    if not request:
        return InteractionInfo.empty()

    matchers = [
        MetadataPathMatcher,
        ReadPathMatcher,
        VReadPathMatcher,
        CreatePathMatcher,
        SearchPathMatcher,
        UpdatePathMatcher,
        PatchPathMatcher,
        DeletePathMatcher,
    ]

    for matcher in matchers:
        if match := matcher.match(request.method, request.url.path):
            return match

    return InteractionInfo.empty()
