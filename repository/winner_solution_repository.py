from typing import List, Optional, cast
from loguru import logger
from sqlalchemy import insert, select, delete, UUID, and_
from sqlalchemy.exc import IntegrityError

from infrastructure.db.connection import pg_connection
from persistent.db.winner_solution import WinnerSolution


class WinnerSolutionRepository:
    def __init__(self) -> None:
        self._sessionmaker = pg_connection()

    async def get_all_winner_solutions(self) -> List[WinnerSolution]:
        """
        Получение всех хакатонов.
        """
        stmt = select(WinnerSolution)

        async with self._sessionmaker() as session:
            resp = await session.execute(stmt)

            rows = resp.fetchall()  # Извлекаем все строки
            winner_solutions = [row[0] for row in rows]  # Преобразуем их в список объектов Hacker
            return winner_solutions

    async def create_winner_solution(
        self,
        hackathon_id: UUID,
        team_id: UUID,
        win_money: float,
        link_to_solution: str,
        link_to_presentation: str,
        can_share: bool = True,
    ) -> Optional[UUID]:
        """
        Создание нового призерского решения.
        """
        stmt = insert(WinnerSolution).values({
            "hackathon_id": hackathon_id,
            "team_id": team_id,
            "win_money": win_money,
            "link_to_solution": link_to_solution,
            "link_to_presentation": link_to_presentation,
            "can_share": can_share,
        })

        async with self._sessionmaker() as session:
            # Добавление хакера
            result = await session.execute(stmt)
            winner_solution_id = result.inserted_primary_key[0]
            try:
                await session.commit()
            except IntegrityError as error:
                await session.rollback()
                return None

        return winner_solution_id

    async def get_winner_solution_by_id(self, solution_id: UUID) -> Optional[WinnerSolution]:
        """
        Получение призерского решения по ID.
        """
        stmt = select(WinnerSolution).where(cast("ColumnElement[bool]", WinnerSolution.id == solution_id))

        async with self._sessionmaker() as session:
            resp = await session.execute(stmt)

        row = resp.fetchone()
        return row[0] if row else None

    async def get_winner_solutions_by_hackathon(self, hackathon_id: UUID) -> List[WinnerSolution]:
        """
        Получение всех призерских решений для конкретного хакатона.
        """
        stmt = select(WinnerSolution).where(WinnerSolution.hackathon.id == hackathon_id)

        async with self._sessionmaker() as session:
            resp = await session.execute(stmt)

        rows = resp.fetchall()
        return [row[0] for row in rows]

    async def get_winner_solutions_by_team(self, team_id: UUID) -> List[WinnerSolution]:
        """
        Получение всех призерских решений для конкретного хакатона.
        """
        stmt = select(WinnerSolution).where(WinnerSolution.team.id == team_id)

        async with self._sessionmaker() as session:
            resp = await session.execute(stmt)

        rows = resp.fetchall()
        return [row[0] for row in rows]

    async def get_winner_solutions_by_team_and_hackathon(self, team_id: UUID, hackathon_id: UUID) -> Optional[WinnerSolution]:
        """
        Получение всех призерских решений для конкретного хакатона.
        """
        stmt = (select(WinnerSolution)
                .where(and_(WinnerSolution.team.id == team_id, WinnerSolution.hackathon.id == hackathon_id)).limit(1))

        async with self._sessionmaker() as session:
            resp = await session.execute(stmt)
            row = resp.fetchall()

            return row[0] if row else None
