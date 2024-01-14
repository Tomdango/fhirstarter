"""Test FHIR utils"""

import pytest

from ..routing import InteractionInfo, parse_fhir_request
from .utils import generate_fhir_resource_id, make_request


@pytest.mark.parametrize(
    argnames="mount_path",
    argvalues=["", "/subapi"],
    ids=["without mount", "with mount"],
)
@pytest.mark.parametrize(
    argnames="_,request_method,path,expected_result",
    argvalues=(
        argvalues := [
            (
                "capabilitites",
                "GET",
                "/metadata",
                InteractionInfo(
                    resource_type=None,
                    interaction_type="capabilities",
                    resource_id=None,
                    version_id=None,
                ),
            ),
            (
                "create",
                "POST",
                "/Patient",
                InteractionInfo(
                    resource_type="Patient",
                    interaction_type="create",
                    resource_id=None,
                    version_id=None,
                ),
            ),
            (
                "read",
                "GET",
                f"/Patient/{(id_ := generate_fhir_resource_id())}",
                InteractionInfo(
                    resource_type="Patient",
                    interaction_type="read",
                    resource_id=id_,
                    version_id=None,
                ),
            ),
            (
                "vread",
                "GET",
                f"/Patient/{(id_ := generate_fhir_resource_id())}/_history/{(vid_ := generate_fhir_resource_id())}",
                InteractionInfo(
                    resource_type="Patient",
                    interaction_type="vread",
                    resource_id=id_,
                    version_id=vid_,
                ),
            ),
            (
                "search-type",
                "GET",
                "/Patient",
                InteractionInfo(
                    resource_type="Patient",
                    interaction_type="search-type",
                    resource_id=None,
                    version_id=None,
                ),
            ),
            (
                "search-type post",
                "POST",
                "/Patient/_search",
                InteractionInfo(
                    resource_type="Patient",
                    interaction_type="search-type",
                    resource_id=None,
                    version_id=None,
                ),
            ),
            (
                "update",
                "PUT",
                f"/Patient/{(id_ := generate_fhir_resource_id())}",
                InteractionInfo(
                    resource_type="Patient",
                    interaction_type="update",
                    resource_id=id_,
                    version_id=None,
                ),
            ),
            (
                "patch",
                "PATCH",
                f"/Patient/{(id_ := generate_fhir_resource_id())}",
                InteractionInfo(
                    resource_type="Patient",
                    interaction_type="patch",
                    resource_id=id_,
                    version_id=None,
                ),
            ),
            (
                "delete",
                "DELETE",
                f"/Patient/{(id_ := generate_fhir_resource_id())}",
                InteractionInfo(
                    resource_type="Patient",
                    interaction_type="delete",
                    resource_id=id_,
                    version_id=None,
                ),
            ),
            (
                "read unrecognized resource type",
                "GET",
                f"/FakeResource/{(id_ := generate_fhir_resource_id())}",
                InteractionInfo(
                    resource_type=None,
                    interaction_type=None,
                    resource_id=None,
                    version_id=None,
                ),
            ),
            (
                "search unrecognized resource type",
                "GET",
                "/FakeResource",
                InteractionInfo(
                    resource_type=None,
                    interaction_type=None,
                    resource_id=None,
                    version_id=None,
                ),
            ),
            (
                "unrecognized GET path",
                "GET",
                f"/Patient/{(id_ := generate_fhir_resource_id())}/extra",
                InteractionInfo(
                    resource_type=None,
                    interaction_type=None,
                    resource_id=None,
                    version_id=None,
                ),
            ),
            (
                "create unrecognized resource type",
                "POST",
                "/FakeResource",
                InteractionInfo(
                    resource_type=None,
                    interaction_type=None,
                    resource_id=None,
                    version_id=None,
                ),
            ),
            (
                "search POST unrecognized resource type",
                "POST",
                "/FakeResource/_search",
                InteractionInfo(
                    resource_type=None,
                    interaction_type=None,
                    resource_id=None,
                    version_id=None,
                ),
            ),
            (
                "unrecognized POST path",
                "POST",
                "/FakeResource/extra",
                InteractionInfo(
                    resource_type=None,
                    interaction_type=None,
                    resource_id=None,
                    version_id=None,
                ),
            ),
            (
                "update unrecognized resource type",
                "PUT",
                f"/FakeResource/{(id_ := generate_fhir_resource_id())}",
                InteractionInfo(
                    resource_type=None,
                    interaction_type=None,
                    resource_id=None,
                    version_id=None,
                ),
            ),
            (
                "unrecognized PUT path",
                "PUT",
                f"/FakeResource/{(id_ := generate_fhir_resource_id())}/extra",
                InteractionInfo(
                    resource_type=None,
                    interaction_type=None,
                    resource_id=None,
                    version_id=None,
                ),
            ),
            (
                "unsupported HTTP method",
                "HEAD",
                f"/Patient/{(id_ := generate_fhir_resource_id())}/extra",
                InteractionInfo(
                    resource_type=None,
                    interaction_type=None,
                    resource_id=None,
                    version_id=None,
                ),
            ),
        ]
    ),
    ids=[id_ for id_, *_ in argvalues],
)
def test_parse_fhir_request(
    _: str,
    mount_path: str,
    request_method: str,
    path: str,
    expected_result: InteractionInfo,
) -> None:
    assert (
        parse_fhir_request(make_request(request_method, f"{mount_path}{path}"))
        == expected_result
    )
