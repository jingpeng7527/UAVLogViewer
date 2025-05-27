from typing import Dict, List, Any
import numpy as np
from datetime import datetime

class MavlinkDataProcessor:
    def __init__(self):
        self.flight_data = {}
        self.messages = {}

    def process_log_data(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw MAVLink log data into a structured format for the chatbot."""
        processed_data = {
            "flight_summary": self._generate_flight_summary(log_data),
            "critical_events": self._find_critical_events(log_data),
            "performance_metrics": self._calculate_performance_metrics(log_data)
        }
        return processed_data

    def _generate_flight_summary(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the flight data."""
        summary = {
            "start_time": None,
            "end_time": None,
            "max_altitude": 0,
            "max_speed": 0,
            "total_distance": 0,
            "flight_duration": 0
        }

        if "GPS" in log_data:
            gps_data = log_data["GPS"]
            if len(gps_data) > 0:
                summary["start_time"] = gps_data[0].get("timestamp")
                summary["end_time"] = gps_data[-1].get("timestamp")
                summary["max_altitude"] = max(point.get("alt", 0) for point in gps_data)
                summary["max_speed"] = max(point.get("vel", 0) for point in gps_data)

        return summary

    def _find_critical_events(self, log_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify critical events during the flight."""
        critical_events = []

        # Check for GPS signal loss
        if "GPS" in log_data:
            gps_data = log_data["GPS"]
            for i, point in enumerate(gps_data):
                if point.get("fix_type", 0) < 3:  # GPS fix type less than 3D fix
                    critical_events.append({
                        "type": "GPS_SIGNAL_LOSS",
                        "timestamp": point.get("timestamp"),
                        "description": "GPS signal quality degraded"
                    })

        # Check for RC signal loss
        if "RCIN" in log_data:
            rcin_data = log_data["RCIN"]
            for i, point in enumerate(rcin_data):
                if point.get("status", 0) == 0:  # Assuming 0 means no signal
                    critical_events.append({
                        "type": "RC_SIGNAL_LOSS",
                        "timestamp": point.get("timestamp"),
                        "description": "RC signal lost"
                    })

        # Check for battery warnings
        if "BAT" in log_data:
            bat_data = log_data["BAT"]
            for i, point in enumerate(bat_data):
                if point.get("voltage", 0) < 3.3:  # Assuming 3.3V per cell is critical
                    critical_events.append({
                        "type": "LOW_BATTERY",
                        "timestamp": point.get("timestamp"),
                        "description": f"Low battery voltage: {point.get('voltage')}V"
                    })

        return critical_events

    def _calculate_performance_metrics(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate various performance metrics from the flight data."""
        metrics = {
            "average_speed": 0,
            "max_battery_temp": 0,
            "average_power_consumption": 0,
            "flight_mode_changes": []
        }

        if "GPS" in log_data:
            gps_data = log_data["GPS"]
            speeds = [point.get("vel", 0) for point in gps_data]
            metrics["average_speed"] = np.mean(speeds) if speeds else 0

        if "BAT" in log_data:
            bat_data = log_data["BAT"]
            temps = [point.get("temperature", 0) for point in bat_data]
            metrics["max_battery_temp"] = max(temps) if temps else 0

        if "MODE" in log_data:
            mode_data = log_data["MODE"]
            current_mode = None
            for point in mode_data:
                if point.get("mode") != current_mode:
                    metrics["flight_mode_changes"].append({
                        "timestamp": point.get("timestamp"),
                        "mode": point.get("mode")
                    })
                    current_mode = point.get("mode")

        return metrics 