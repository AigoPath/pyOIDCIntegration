from typing import Any

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2
from fastapi.openapi.models import OAuthFlowAuthorizationCode, OAuthFlows

from . import Auth
from .lru_timeout_cache import LRUTimeoutCache

class AuthSettings(BaseSettings):
    idp_url: str
    audience: str
    refresh_interval: int = 300  # seconds
    openapi_token_url: str = ""
    openapi_auth_url: str = ""
    rewrite_url_in_wellknown: str = ""

    # Authorization Data Caching
    user_cache_timeout: int = 1800
    user_cache_size: int = 999
    user_info_endpoint: str = ""  # Url to the user info data, e.g. 'https://login.bbmri-eric.eu/oidc/userinfo'

    model_config = SettingsConfigDict(env_prefix="wbs_", env_file=".env")


class TokenPayload(BaseModel):
    payload: str
    data: dict


class Payload(BaseModel):
    token: TokenPayload
    request: Any = None


def make_oauth2_wrapper(auth: Auth, auth_settings: AuthSettings):
    oauth2_scheme = OAuth2(
        flows=OAuthFlows(
            authorizationCode=OAuthFlowAuthorizationCode(
                tokenUrl=auth_settings.openapi_token_url, authorizationUrl=auth_settings.openapi_auth_url
            )
        )
    )

    def oauth2_wrapper(request: Request, token=Depends(oauth2_scheme)):
        decoded_token = auth.decode_token(token)
        token_payload = TokenPayload(payload=token, data=decoded_token)
        return Payload(token=token_payload, request=request)

    return oauth2_wrapper


class OAuthIntegration:
    def __init__(self, settings, logger=None):
        self.settings = settings
        self.logger = logger
        self.auth_settings = AuthSettings()

        self.auth = Auth(
            idp_url=self.auth_settings.idp_url.rstrip("/"),
            refresh_interval=self.auth_settings.refresh_interval,
            audience=self.auth_settings.audience,
            logger=self.logger,
            rewrite_url_in_wellknown=self.auth_settings.rewrite_url_in_wellknown,
        )
        self.oauth2_wrapper = make_oauth2_wrapper(auth=self.auth, auth_settings=self.auth_settings)
        self.user_cache = LRUTimeoutCache(self.auth_settings.user_cache_size, self.auth_settings.user_cache_timeout)

    def global_depends(self):
        return Depends(self.oauth2_wrapper)
