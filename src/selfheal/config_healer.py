import json
from typing import Optional
from pathlib import Path
from typing import Type, TypeVar
import structlog
from pydantic_settings import BaseSettings

logger = structlog.get_logger(__name__)

T = TypeVar("T", bound="SelfHealingConfig")

class SelfHealingConfig(BaseSettings):
    """
    Pydantic BaseSettings subclass that self-heals its configuration file.
    It will auto-regenerate missing files, backup+repair corrupt ones,
    and raise explicitly for missing secrets.
    """

    @classmethod
    def load_or_heal(
        cls: Type[T],
        config_path: str,
        sensitive_fields: Optional[list[str]] = None
    ) -> T:
        sensitive_fields = sensitive_fields or []
        path = Path(config_path)

        # 1. Regenerate missing config
        if not path.exists():
            logger.warning("Config file missing, generating defaults", path=config_path)
            return cls._generate_and_save(path, sensitive_fields)

        # 2. Try loading
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            return cls(**data)
        except json.JSONDecodeError as e:
            logger.error("Config file is corrupt, backing up and regenerating", path=config_path, error=str(e))
            return cls._backup_and_regenerate(path, sensitive_fields)
        except Exception as e:
            # Catch pydantic validation errors
            logger.error("Config validation failed, attempting field-level repair", path=config_path, error=str(e))
            return cls._repair_fields(path, sensitive_fields)

    @classmethod
    def _generate_and_save(cls: Type[T], path: Path, sensitive_fields: list[str]) -> T:
        # Pydantic will pull from defaults or environment variables
        try:
            instance = cls()
        except ValueError as e:
            logger.critical("Cannot generate default config. Missing sensitive/required fields?", error=str(e))
            raise

        cls._save(instance, path)
        return instance

    @classmethod
    def _backup_and_regenerate(cls: Type[T], path: Path, sensitive_fields: list[str]) -> T:
        backup_path = path.with_suffix('.bak')
        if path.exists():
            path.rename(backup_path)
        return cls._generate_and_save(path, sensitive_fields)

    @classmethod
    def _repair_fields(cls: Type[T], path: Path, sensitive_fields: list[str]) -> T:
        try:
            with open(path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            return cls._backup_and_regenerate(path, sensitive_fields)

        # Field-level repair: Generate defaults, and override with valid keys from data
        try:
            defaults = cls().model_dump()
        except ValueError as e:
             logger.critical("Cannot repair config due to missing sensitive/required fields in env", error=str(e))
             raise

        for key, value in data.items():
            if key in defaults:
                original_value = defaults[key]
                try:
                    defaults[key] = value
                    # Verify it's valid for this field by constructing a dummy model
                    cls(**defaults)
                except Exception:
                    logger.warning("Discarding invalid field value during repair", field=key)
                    defaults[key] = original_value

        try:
            instance = cls(**defaults)
            cls._save(instance, path)
            return instance
        except Exception as e:
            logger.error("Field-level repair failed, falling back to full regeneration", error=str(e))
            return cls._backup_and_regenerate(path, sensitive_fields)

    @classmethod
    def _save(cls, instance: "SelfHealingConfig", path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(instance.model_dump(mode='json'), f, indent=2)
