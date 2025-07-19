from homeassistant.components.http import HomeAssistantView
from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.util import session_scope
from homeassistant.components.recorder.db_schema import Statistics, StatisticsMeta
from homeassistant.util import dt as dt_util
from datetime import datetime, timedelta, timezone

class LongTermStatsView(HomeAssistantView):
    url = "/api/long_term_stats"
    name = "api:long_term_stats"
    requires_auth = True

    async def get(self, request):
        hass = request.app["hass"]
        entity_id = request.query.get("entity_id")
        datetime_str = request.query.get("datetime")
        end_datetime_str = request.query.get("end_datetime")

        if not entity_id or not datetime_str:
            return self.json_message("Missing 'entity_id' or 'datetime'", status_code=400)

        try:
            input_dt = datetime.fromisoformat(datetime_str)
        except ValueError:
            return self.json_message(
                "Invalid datetime format (use YYYY-MM-DDTHH:MM:SS)", status_code=400
            )
        # Query for single datetime
        if not end_datetime_str:
            utc_dt = dt_util.as_utc(input_dt)
            hour_start = utc_dt.replace(minute=0, second=0, microsecond=0)
            hour_end = hour_start + timedelta(hours=1)
            start_ts_start = int(hour_start.replace(tzinfo=timezone.utc).timestamp())
            start_ts_end = int(hour_end.replace(tzinfo=timezone.utc).timestamp())

            # Run database work safely in executor thread
            def query():
                instance = get_instance(hass)
                with session_scope(session=instance.get_session()) as session:
                    meta_raw = session.query(StatisticsMeta).filter_by(statistic_id=entity_id).first()

                    if not meta_raw:
                        return self.json({"error": "Entity not found"}, status_code=404)

                    stat_raw = (
                        session.query(Statistics)
                        .filter(
                            Statistics.metadata_id == meta_raw.id,
                            Statistics.start_ts >= start_ts_start,
                            Statistics.start_ts < start_ts_end,
                        )
                        .first()
                    )

                    if not stat_raw:
                        return self.json({"message": "No statistics found for that hour"}, status_code=404)

                    return self.json_message({
                            "start_ts": stat_raw.start_ts,
                            "mean": stat_raw.mean,
                            "min": stat_raw.min,
                            "max": stat_raw.max,
                            "sum": stat_raw.sum,
                            "state": stat_raw.state,
                        }, status_code=200)

            return await get_instance(hass).async_add_executor_job(query)

        # Query for several date time
        else:
            utc_dt = dt_util.as_utc(input_dt)
            hour_start = utc_dt.replace(minute=0, second=0, microsecond=0)
            start_ts_start = int(hour_start.replace(tzinfo=timezone.utc).timestamp())

            try:
                input_dt_end = datetime.fromisoformat(end_datetime_str)
            except ValueError:
                return self.json_message(
                    "Invalid end datetime format (use YYYY-MM-DDTHH:MM:SS)", status_code=400
                )
            utc_dt_end = dt_util.as_utc(input_dt_end)
            hour_end = utc_dt_end.replace(minute=0, second=0, microsecond=0)
            start_ts_end = int(hour_end.replace(tzinfo=timezone.utc).timestamp())

            # Run database work safely in executor thread
            def query():
                instance = get_instance(hass)
                with session_scope(session=instance.get_session()) as session:
                    meta_raw = session.query(StatisticsMeta).filter_by(statistic_id=entity_id).first()

                    if not meta_raw:
                        return self.json({"error": "Entity not found"}, status_code=404)

                    stat_raw_list = (
                        session.query(Statistics)
                        .filter(
                            Statistics.metadata_id == meta_raw.id,
                            Statistics.start_ts >= start_ts_start,
                            Statistics.start_ts < start_ts_end,
                        )
                        .all()
                    )

                    if not stat_raw_list:
                        return self.json({"message": "No statistics found for that dates"}, status_code=404)

                    return self.json_message([{
                            "start_ts": stat_raw.start_ts,
                            "mean": stat_raw.mean,
                            "min": stat_raw.min,
                            "max": stat_raw.max,
                            "sum": stat_raw.sum,
                            "state": stat_raw.state,
                        }
                        for stat_raw in stat_raw_list
                        ], status_code=200)

            return await get_instance(hass).async_add_executor_job(query)