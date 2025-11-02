"""
Configuración para la conexión a Azure Identity.

Permite configurar la conexión a Azure, incluyendo el ID de la suscripción,
el ID del tenant, y la región de Azure.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class IdentitySettings(BaseSettings):
    """
    Configuración de la conexión a Azure.

    - subscription_id: ID de la suscripción de Azure
    - tenant_id: ID del tenant de Azure
    - region: Región de Azure
    """

    model_config = SettingsConfigDict(extra='ignore', case_sensitive=False)
    subscription_id: str | None = Field(validation_alias='SUBSCRIPTION_ID')
    tenant_id: str | None = Field(validation_alias='TENANT_ID')
    region: str | None = Field(validation_alias='REGION')
