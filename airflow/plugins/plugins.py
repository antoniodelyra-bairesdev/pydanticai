from airflow.plugins_manager import AirflowPlugin
from WorkdayHolidayTimetable import WorkdayHolidayTimetable


class WorkdayHolidayTimetablePlugin(AirflowPlugin):
    name = "workday_holiday_timetable_plugin"
    timetables = [WorkdayHolidayTimetable]
