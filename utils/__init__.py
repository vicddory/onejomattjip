# -*- coding: utf-8 -*-
"""
================================================================================
📁 utils/__init__.py - 유틸리티 패키지
================================================================================
이 파일은 utils 폴더를 Python 패키지로 만들어줍니다.
다른 파일에서 쉽게 import할 수 있도록 주요 함수들을 노출합니다.

💡 사용 예시:
    from utils import get_exchange_rate, get_market_data
================================================================================
"""

from .api_helpers import (
    get_exchange_rate,
    get_exchange_rate_with_status,
    get_current_local_rate,
    get_market_data,
    get_history_rate,
    get_country_weather
)

__all__ = [
    'get_exchange_rate',
    'get_exchange_rate_with_status',
    'get_current_local_rate',
    'get_market_data',
    'get_history_rate',
    'get_country_weather'
]
