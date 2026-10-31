class SettingsLoader:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_defaults()
        return cls._instance

    def _load_defaults(self):
        self._settings = {
            "DATA_DIR": "data",
            "USERS_FILE": "data/users.json",
            "PORTFOLIOS_FILE": "data/portfolios.json",
            "RATES_FILE": "data/rates.json",
            "SESSION_FILE": "data/session.json",
            "RATES_TTL_SECONDS": 300,  # 5 минут
            "BASE_CURRENCY": "USD",
            "LOG_LEVEL": "INFO",
            "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        }

    def get(self, key: str, default=None):
        return self._settings.get(key, default)

    def reload(self):
        self._load_defaults()
        print("Настройки перезагружены.")

    @property
    def DATA_DIR(self):
        return self.get("DATA_DIR")

    @property
    def USERS_FILE(self):
        return self.get("USERS_FILE")

    @property
    def PORTFOLIOS_FILE(self):
        return self.get("PORTFOLIOS_FILE")

    @property
    def RATES_FILE(self):
        return self.get("RATES_FILE")

    @property
    def SESSION_FILE(self):
        return self.get("SESSION_FILE")

    @property
    def RATES_TTL_SECONDS(self):
        return self.get("RATES_TTL_SECONDS")

    @property
    def BASE_CURRENCY(self):
        return self.get("BASE_CURRENCY")

    @property
    def LOG_LEVEL(self):
        return self.get("LOG_LEVEL")

    @property
    def LOG_FORMAT(self):
        return self.get("LOG_FORMAT")