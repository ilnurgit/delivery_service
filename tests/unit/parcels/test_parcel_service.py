from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from delivery.parcel_types.domain.errors import ParcelTypeNotFoundError
from delivery.parcels.domain.errors import ParcelWeightMustBePositiveError
from delivery.parcels.services.service import ParcelService

pytestmark = pytest.mark.unit


@dataclass(slots=True)
class _ParcelType:
    id: str
    code: str
    name: str
    base_price_usd: str
    price_per_kg_usd: str


class FakeParcelRepo:
    def __init__(self) -> None:
        self.created: list[Any] = []

    async def create(self, parcel):
        self.created.append(parcel)
        return parcel

    async def get_by_id_for_session(self, parcel_id: str, session_id: str):
        raise AssertionError("not used in these tests")

    async def list_for_session(
        self, session_id: str, *, limit: int, offset: int, has_cost: bool | None
    ):
        raise AssertionError("not used in these tests")


class FakeParcelTypeRepo:
    def __init__(self, existing: dict[str, _ParcelType] | None = None) -> None:
        self._existing = existing or {}

    async def get_by_code(self, code: str):
        return self._existing.get(code)


async def test_create_parcel_negative_weight_raises():
    service = ParcelService(
        repo=FakeParcelRepo(),
        type_repo=FakeParcelTypeRepo(
            existing={"DOC": _ParcelType("pt-1", "DOC", "Documents", "5.00", "2.50")}
        ),
    )

    with pytest.raises(ParcelWeightMustBePositiveError):
        await service.create_parcel(
            session_id="s1",
            parcel_type_code="DOC",
            title="Passport",
            weight_kg=-1,
            content_usd="10.00",
        )


async def test_create_parcel_unknown_type_raises():
    service = ParcelService(
        repo=FakeParcelRepo(),
        type_repo=FakeParcelTypeRepo(existing={}),  # типа нет
    )

    with pytest.raises(ParcelTypeNotFoundError):
        await service.create_parcel(
            session_id="s1",
            parcel_type_code="DOC",
            title="Passport",
            weight_kg=1,
            content_usd="10.00",
        )


async def test_create_parcel_success_sets_fields():
    repo = FakeParcelRepo()
    service = ParcelService(
        repo=repo,
        type_repo=FakeParcelTypeRepo(
            existing={"DOC": _ParcelType("pt-1", "DOC", "Documents", "5.00", "2.50")}
        ),
    )

    parcel = await service.create_parcel(
        session_id="s1",
        parcel_type_code="DOC",
        title="Passport",
        weight_kg=2,
        content_usd="100.00",
    )

    assert parcel.session_id == "s1"
    assert parcel.parcel_type_id == "pt-1"
    assert parcel.title == "Passport"
    assert parcel.weight_kg == 2
    assert parcel.content_usd == "100.00"
    assert parcel.delivery_cost_rub is None
    assert len(repo.created) == 1
    assert repo.created[0].id == parcel.id
