from __future__ import annotations

from delivery.parcel_types.domain.entities import ParcelType
from delivery.parcel_types.repositories.sqlalchemy import SqlAlchemyParcelTypeRepository


class ParcelTypeService:
    def __init__(self, repo: SqlAlchemyParcelTypeRepository) -> None:
        self._repo = repo

    async def list_types(self) -> list[ParcelType]:
        return await self._repo.list_all()

    async def get_type(self, code: str) -> ParcelType | None:
        return await self._repo.get_by_code(code)

    async def create_type(self, code: str, name: str) -> ParcelType:
        return await self._repo.create(code=code, name=name)
