from typing import Type, TypeVar, List, Optional

from sqlalchemy import insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import Base, CurrenciesPairs
from schemas import CurrenciesPairsCreateDB, CurreciesPairsUpdate

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase:
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(self, db: AsyncSession, create_schema: CurrenciesPairsCreateDB) -> ModelType:
        data = create_schema.model_dump(exclude_unset=True)
        stmt = insert(self.model).values(**data).returning(self.model)
        res = await db.execute(stmt)
        obj = res.scalars().first()
        await db.commit()
        await db.refresh(obj)
        return obj

    async def read_user_pairs(self, db: AsyncSession, tg_id: int) -> Optional[List[ModelType]]:
        stmt = select(self.model).where(self.model.user_tg_id == tg_id)
        result = await db.execute(stmt)

        return result.scalars().all()

    async def update(
        self, db: AsyncSession, obj_id: int, update_schema: CurreciesPairsUpdate
    ) -> Optional[ModelType]:
        obj = await db.get(db, obj_id)
        if obj:
            data = update_schema.model_dump(exclude_unset=True)
            stmt = (
                update(self.model)
                .where(self.model.id == obj_id)
                .values(**data)
                .returning(self.model)
            )
        res = await db.execute(stmt)
        obj = res.scalars().first()
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(self, db: AsyncSession, obj_id: int) -> Optional[ModelType]:
        obj = await db.get(self.model, obj_id)
        if not obj:
            return None
        await db.delete(obj)
        await db.commit()
        return obj

    async def read_all(self, db: AsyncSession) -> List[ModelType]:
        result = await db.execute(select(self.model))
        return result.scalars().all()


currrencies_crud = CRUDBase(CurrenciesPairs)
