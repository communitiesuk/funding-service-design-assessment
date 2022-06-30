from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class UnitTestConfig(DefaultConfig):
    FORCE_HTTPS = False

    TALISMAN_SETTINGS = {
        "feature_policy": DefaultConfig.FSD_FEATURE_POLICY,
        "permissions_policy": DefaultConfig.FSD_PERMISSIONS_POLICY,
        "document_policy": DefaultConfig.FSD_DOCUMENT_POLICY,
        "force_https": FORCE_HTTPS,
        "force_https_permanent": False,
        "force_file_save": False,
        "frame_options": "SAMEORIGIN",
        "frame_options_allow_from": None,
        "strict_transport_security": True,
        "strict_transport_security_preload": True,
        "strict_transport_security_max_age": DefaultConfig.ONE_YEAR_IN_SECS,
        "strict_transport_security_include_subdomains": True,
        "content_security_policy": DefaultConfig.SECURE_CSP,
        "content_security_policy_report_uri": None,
        "content_security_policy_report_only": False,
        "content_security_policy_nonce_in": None,
        "referrer_policy": DefaultConfig.FSD_REFERRER_POLICY,
        "session_cookie_secure": True,
        "session_cookie_http_only": True,
        "session_cookie_samesite": DefaultConfig.FSD_SESSION_COOKIE_SAMESITE,
        "x_content_type_options": True,
        "x_xss_protection": True,
    }
