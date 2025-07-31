import pendulum
from typing import Optional, Dict, Any

from airflow.timetables.base import DagRunInfo, DataInterval, TimeRestriction, Timetable


class WorkdayHolidayTimetable(Timetable):
    """
    Agenda DAGs para rodar em um horário específico apenas em dias úteis
    (Segunda a Sexta), excluindo uma lista de feriados fornecida.

    O data_interval será de 24h começando no schedule_time do dia útil válido.
    O run_after será o final desse data_interval.
    """

    def __init__(
        self,
        holidays: list[str],
        schedule_hour: int = 0,
        schedule_minute: int = 0,
        timezone_str: str = "UTC",
    ):
        self.schedule_hour = schedule_hour
        self.schedule_minute = schedule_minute
        self.timezone_str = timezone_str
        self._timezone = pendulum.timezone(timezone_str)

        self._parsed_holidays = set()
        for holiday_str in holidays:
            try:
                self._parsed_holidays.add(pendulum.parse(holiday_str).date())  # type: ignore
            except Exception as e:
                print(
                    f"Aviso: Não foi possível parsear a data de feriado '{holiday_str}': {e}"
                )

        self.holiday_date_strings = holidays  # Para serialização
        super().__init__()

    @property
    def summary(self) -> str:
        return f"Dias úteis (exceto {len(self._parsed_holidays)} feriados) às {self.schedule_hour:02d}:{self.schedule_minute:02d} {self.timezone_str}"

    def serialize(self) -> Dict[str, Any]:
        return {
            "holidays": self.holiday_date_strings,
            "schedule_hour": self.schedule_hour,
            "schedule_minute": self.schedule_minute,
            "timezone_str": self.timezone_str,
        }

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "Timetable":
        return cls(
            holidays=data["holidays"],
            schedule_hour=data["schedule_hour"],
            schedule_minute=data["schedule_minute"],
            timezone_str=data["timezone_str"],
        )

    def infer_manual_data_interval(
        self, *, run_after: pendulum.DateTime
    ) -> DataInterval:
        """
        Para runs manuais, encontra o dia útil válido mais recente (ou o atual).
        Caso a DAG tenha sido acionada manualmente em um dia não útil, busca o primeiro dia útil anterior
        """
        # run_after é o momento do trigger, geralmente em UTC. É preciso trabalhar na timezone do schedule
        current_trigger_time = run_after.in_timezone(self._timezone)

        slot_candidate = self._align_to_schedule_time(current_trigger_time)
        if slot_candidate > current_trigger_time or not self._is_valid_schedule_day(
            slot_candidate
        ):
            search_day = current_trigger_time.subtract(days=1)
        else:
            search_day = current_trigger_time

        # Encontra o dia útil/não feriado mais recente, alinhado ao horário
        aligned_search_day = self._align_to_schedule_time(search_day)
        while not self._is_valid_schedule_day(aligned_search_day):
            aligned_search_day = self._align_to_schedule_time(
                aligned_search_day.subtract(days=1)
            )

        data_interval_start = aligned_search_day
        data_interval_end = data_interval_start.add(days=1)

        return DataInterval(start=data_interval_start, end=data_interval_end)

    def next_dagrun_info(
        self,
        *,
        last_automated_data_interval: Optional[DataInterval],
        restriction: TimeRestriction,
    ) -> Optional[DagRunInfo]:
        if restriction.earliest is None:
            # DAG não tem start_date, não podemos agendar.
            return None

        if last_automated_data_interval is None:
            # Primeira execução: o ponto de partida é o start_date da DAG.
            candidate_start_time = restriction.earliest.in_timezone(self._timezone)
        else:
            candidate_start_time = last_automated_data_interval.end.in_timezone(
                self._timezone
            ).add(microseconds=1)

        # Alinha o candidato ao horário do schedule do dia.
        # Se o start_date (ou fim do último run) for 10:00 e o schedule é 09:00,
        # o primeiro `next_schedule_attempt` será HOJE às 09:00.
        # Se o start_date for 08:00 e o schedule é 09:00, o primeiro `next_schedule_attempt`
        # também será HOJE às 09:00.
        next_schedule_attempt = self._align_to_schedule_time(candidate_start_time)

        # Loop para encontrar o próximo dia válido no horário agendado
        while True:
            # Se o horário de tentativa é antes do nosso ponto de partida real (candidate_start_time),
            # significa que já passamos do horário agendado para este dia.
            # Precisamos avançar para o horário agendado do próximo dia.
            if next_schedule_attempt < candidate_start_time:
                next_schedule_attempt = self._align_to_schedule_time(
                    next_schedule_attempt.add(days=1)
                )
                continue  # Recomeça a verificação para o novo dia

            if self._is_valid_schedule_day(next_schedule_attempt):
                break  # Sai do loop

            # Se não é válido, tenta o próximo dia no horário agendado.
            next_schedule_attempt = self._align_to_schedule_time(
                next_schedule_attempt.add(days=1)
            )

        # Checa se o próximo run calculado excede o end_date da DAG (se houver)
        # ou o tempo atual se catchup=False.
        if (
            restriction.latest is not None
            and next_schedule_attempt >= restriction.latest.in_timezone(self._timezone)
        ):
            return None

        data_interval_start = next_schedule_attempt
        data_interval_end = data_interval_start.add(days=1)
        run_after_time = data_interval_start

        return DagRunInfo(
            data_interval=DataInterval(
                start=data_interval_start, end=data_interval_end
            ),
            run_after=run_after_time,
        )

    def _is_valid_schedule_day(self, current_date: pendulum.DateTime) -> bool:
        """Verifica se a data é um dia útil e não é feriado."""
        dt_in_tz = current_date.in_timezone(self._timezone)
        # pendulum.DateTime.day_of_week: Monday is 1 and Sunday is 7
        if dt_in_tz.day_of_week >= 6:  # Sábado ou Domingo
            return False
        if dt_in_tz.date() in self._parsed_holidays:
            return False
        return True

    def _align_to_schedule_time(self, dt: pendulum.DateTime) -> pendulum.DateTime:
        """Alinha um datetime para o horário agendado no mesmo dia, na timezone configurada."""
        return dt.in_timezone(self._timezone).set(
            hour=self.schedule_hour,
            minute=self.schedule_minute,
            second=0,
            microsecond=0,
        )
