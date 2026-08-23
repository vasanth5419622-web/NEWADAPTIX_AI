from typing import Dict
from app.core.config import settings
from app.services.models.base import BaseModelProvider
from app.services.models.open_model import OpenWeightModelProvider
from app.services.models.commercial_a import CommercialModelAProvider
from app.services.models.commercial_b import CommercialModelBProvider
from app.services.models.mock_provider import MockAgriculturalProvider

class ModelProviderFactory:
    """
    Factory to retrieve and instantiate model providers dynamically based on settings or runtime overrides.
    """
    @staticmethod
    def get_open_model() -> BaseModelProvider:
        if settings.open_model.provider == "mock":
            return MockAgriculturalProvider(model_name=settings.open_model.name, role="open_weight")
        return OpenWeightModelProvider(
            model_name=settings.open_model.name,
            api_key=settings.open_model.api_key,
            base_url=settings.open_model.base_url
        )

    @staticmethod
    def get_commercial_a() -> BaseModelProvider:
        if settings.commercial_a.provider == "mock":
            return MockAgriculturalProvider(model_name=settings.commercial_a.name, role="commercial_a")
        return CommercialModelAProvider(
            model_name=settings.commercial_a.name,
            api_key=settings.commercial_a.api_key,
            base_url=settings.commercial_a.base_url
        )

    @staticmethod
    def get_commercial_b() -> BaseModelProvider:
        if settings.commercial_b.provider == "mock":
            return MockAgriculturalProvider(model_name=settings.commercial_b.name, role="commercial_b")
        return CommercialModelBProvider(
            model_name=settings.commercial_b.name,
            api_key=settings.commercial_b.api_key,
            base_url=settings.commercial_b.base_url
        )

    @staticmethod
    def get_provider_by_key(key: str) -> BaseModelProvider:
        if key == "open_weight":
            return ModelProviderFactory.get_open_model()
        elif key == "commercial_a":
            return ModelProviderFactory.get_commercial_a()
        elif key == "commercial_b":
            return ModelProviderFactory.get_commercial_b()
        else:
            return MockAgriculturalProvider(model_name="generic-provider", role="open_weight")

model_factory = ModelProviderFactory()
