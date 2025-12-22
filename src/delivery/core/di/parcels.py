from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from delivery.core.di.db import get_db_session
from delivery.parcel_types.repositories.sqlalchemy import SqlAlchemyParcelTypeRepository
from delivery.parcels.repositories.sqlalchemy import SqlAlchemyParcelRepository
from delivery.parcels.services.service import ParcelService


def get_parcel_service(
    session: AsyncSession = Depends(get_db_session),
) -> ParcelService:
    parcel_repo = SqlAlchemyParcelRepository(session)
    type_repo = SqlAlchemyParcelTypeRepository(session)
    return ParcelService(repo=parcel_repo, type_repo=type_repo)
