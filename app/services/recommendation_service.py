from __future__ import annotations
from typing import Sequence, List, Dict
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, literal, and_, not_, desc

from app.models.task_table import Task
from app.models.task_history_table import TaskHistory


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
_SKLEARN = True



@dataclass
class RankedTask:
    id: int
    subject: str
    problem: str
    difficulty: float
    relevance_score: float
    match_reason: str


class RecommendationService:
    def __init__(
            self,
            vectorizer_max_features: int = 1000,
            vectorizer_min_df: int = 2,
            vectorizer_max_df: float = 0.8,
    ) -> None:
        self._use_text = _SKLEARN
        if self._use_text:
            self.vectorizer = TfidfVectorizer(
                stop_words='russian',
                max_features=vectorizer_max_features,
                min_df=vectorizer_min_df,
                max_df=vectorizer_max_df,
            )

    async def get_user_recommendations(
            self,
            session: AsyncSession,
            user_id: int,
            n_recommendations: int = 5,
    ) -> List[RankedTask]:
        user_history = await self._get_user_history(session, user_id)

        if not user_history:
            defaults = await self._get_default_recommendations(session, n_recommendations)
            return defaults

        preferred_subjects = self._analyze_subjects(user_history)
        optimal_difficulty = self._analyze_difficulty(user_history)

        candidate_tasks = await self._get_candidate_tasks(session, user_id, preferred_subjects)
        if not candidate_tasks:
            candidate_tasks = await self._get_all_unsolved_tasks(session, user_id)

        ranked = self._rank_tasks(candidate_tasks, user_history, optimal_difficulty, preferred_subjects)
        return ranked[:n_recommendations]

    async def _get_user_history(self, session: AsyncSession, user_id: int):
        q = (
            select(
                TaskHistory.task_id,
                TaskHistory.status,
                TaskHistory.score,
                Task.subject,
                Task.difficulty,
                Task.problem,
            )
            .join(Task, Task.id == TaskHistory.task_id)
            .where(TaskHistory.user_id == user_id)
            .order_by(TaskHistory.timestamp.desc())
            .limit(50)
        )
        res = (await session.execute(q)).all()
        return res

    def _analyze_subjects(self, user_history: Sequence[tuple]) -> List[str]:
        subject_scores: Dict[str, float] = {}
        for task_id, status, score, subject, difficulty, problem in user_history:
            weight = 1.0
            if status == 'solved':
                weight = 1.5
            elif status == 'attempted':
                weight = 0.7
            subject_scores[subject] = subject_scores.get(subject, 0.0) + (float(score or 0.0) * weight)

        sorted_subjects = sorted(subject_scores.items(), key=lambda x: x[1], reverse=True)
        return [s for s, _ in sorted_subjects[:3]]

    def _analyze_difficulty(self, user_history: Sequence[tuple]) -> float:
        diffs: List[float] = []
        weights: List[float] = []
        for _, status, score, _, difficulty, _ in user_history:
            score = float(score or 0.0)
            if status == 'solved' or score > 0.7:
                diffs.append(float(difficulty or 0.0))
                weights.append(max(score, 0.01))
        if not diffs:
            return 2.5
        # взвешенное среднее
        total_w = sum(weights)
        return sum(d * w for d, w in zip(diffs, weights)) / total_w

    async def _get_candidate_tasks(self, session: AsyncSession, user_id: int, preferred_subjects: List[str]):
        if not preferred_subjects:
            return await self._get_all_unsolved_tasks(session, user_id)

        subq = select(TaskHistory.task_id).where(TaskHistory.user_id == user_id)
        q = (
            select(Task.id, Task.subject, Task.problem, Task.solution, Task.answer, Task.difficulty)
            .where(not_(Task.id.in_(subq)))
            .where(Task.subject.in_(preferred_subjects))
        )
        return (await session.execute(q)).all()

    async def _get_all_unsolved_tasks(self, session: AsyncSession, user_id: int):
        subq = select(TaskHistory.task_id).where(TaskHistory.user_id == user_id)
        q = (
            select(Task.id, Task.subject, Task.problem, Task.solution, Task.answer, Task.difficulty)
            .where(not_(Task.id.in_(subq)))
        )
        return (await session.execute(q)).all()

    def _rank_tasks(
            self,
            candidate_tasks: Sequence[tuple],
            user_history: Sequence[tuple],
            optimal_difficulty: float,
            preferred_subjects: List[str],
    ) -> List[RankedTask]:

        solved_problems = [p for _, st, _, _, _, p in user_history if st == 'solved']
        use_text = self._use_text and len(solved_problems) >= 2

        if use_text:
            try:
                self.vectorizer.fit(solved_problems)
            except Exception:
                use_text = False

        ranked: List[RankedTask] = []
        for t in candidate_tasks:
            task_id, subject, problem, solution, answer, difficulty = t
            difficulty = float(difficulty or 0.0)

            difficulty_score = 1.0 / (1.0 + abs(difficulty - optimal_difficulty))

            subject_score = 1.5 if subject in set(preferred_subjects) else 1.0

            similarity_score = 0.0
            if use_text:
                try:
                    task_vec = self.vectorizer.transform([problem or ""])
                    hist_vec = self.vectorizer.transform(solved_problems)
                    sim = cosine_similarity(task_vec, hist_vec)
                    similarity_score = float(sim.max()) if sim.size else 0.0
                except Exception:
                    similarity_score = 0.0

            total = 0.4 * difficulty_score + 0.3 * subject_score + 0.3 * similarity_score
            ranked.append(
                RankedTask(
                    id=int(task_id),
                    subject=subject,
                    problem=problem,
                    difficulty=difficulty,
                    relevance_score=total,
                    match_reason=self._get_match_reason(difficulty_score, subject_score, similarity_score),
                )
            )

        ranked.sort(key=lambda x: x.relevance_score, reverse=True)
        return ranked

    def _get_match_reason(self, difficulty_score: float, subject_score: float, similarity_score: float) -> str:
        reasons = []
        if difficulty_score > 0.7:
            reasons.append("оптимальная сложность")
        if subject_score > 1.2:
            reasons.append("предпочтительная тема")
        if similarity_score > 0.5:
            reasons.append("похожа на решенные вами задачи")
        return " и ".join(reasons) if reasons else "новый вызов"

    async def _get_default_recommendations(self, session: AsyncSession, n: int) -> List[RankedTask]:
        solved_cte = (
            select(TaskHistory.task_id, func.count(literal(1)).label("cnt"))
            .where(TaskHistory.status == 'solved')
            .group_by(TaskHistory.task_id)
            .cte("solved_counts")
        )
        q = (
            select(
                Task.id, Task.subject, Task.problem, Task.solution, Task.answer, Task.difficulty,
                func.coalesce(solved_cte.c.cnt, 0).label("s_cnt")
            )
            .join(solved_cte, solved_cte.c.task_id == Task.id, isouter=True)
            .where(and_(Task.difficulty >= 2, Task.difficulty <= 3))
            .order_by(desc("s_cnt"), Task.difficulty)
            .limit(n * 2)
        )
        rows = (await session.execute(q)).all()
        out: List[RankedTask] = []
        for r in rows[:n]:
            task_id, subject, problem, solution, answer, difficulty, _ = r
            out.append(
                RankedTask(
                    id=int(task_id),
                    subject=subject,
                    problem=problem,
                    difficulty=float(difficulty or 0.0),
                    relevance_score=0.5,
                    match_reason="популярная задача средней сложности",
                )
            )
        return out
