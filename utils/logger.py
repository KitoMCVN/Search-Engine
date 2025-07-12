from datetime import datetime

class ConsoleLogger:
    COLOR_MAP = {
        "INFO": "\033[32m",
        "WARN": "\033[33m",
        "ERROR": "\033[31m", 
        "DEBUG": "\033[36m", 
        "RESET": "\033[0m"   
    }

    EMOJI_MAP = {
        "INFO": "🟩",
        "WARN": "🟨",
        "ERROR": "🟥",
        "DEBUG": "🟦"
    }

    def _now(self):
        return datetime.now().strftime("%H:%M:%S")

    def _log(self, level: str, message: str):
        emoji = self.EMOJI_MAP.get(level, "")
        color = self.COLOR_MAP.get(level, "")
        reset = self.COLOR_MAP["RESET"]
        time_str = f"[{self._now()}]"
        level_str = f"[{level:<5}]"
        level_colored = f"{color}{level_str}{reset}"
        print(f"{emoji} {time_str} {level_colored} {message}")

    def info(self, message: str):
        self._log("INFO", message)

    def warn(self, message: str):
        self._log("WARN", message)

    def error(self, message: str):
        self._log("ERROR", message)

    def debug(self, message: str):
        self._log("DEBUG", message)