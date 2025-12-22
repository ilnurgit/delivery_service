from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from delivery.core.di.db import get_db_session
from delivery.parcels.repositories.sqlalchemy import SqlAlchemyParcelRepository
from delivery.parcels.services.service import ParcelService


def get_parcel_service(
    session: AsyncSession = Depends(get_db_session),
) -> ParcelService:
    repo = SqlAlchemyParcelRepository(session)
    return ParcelService(repo=repo)
