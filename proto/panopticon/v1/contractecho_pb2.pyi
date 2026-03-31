import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListingWire(_message.Message):
    __slots__ = ("id", "tenant_id", "seller_id", "title", "description", "listing_type", "price_type", "price_amount", "metadata_json", "sku")
    ID_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    SELLER_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LISTING_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRICE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRICE_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    METADATA_JSON_FIELD_NUMBER: _ClassVar[int]
    SKU_FIELD_NUMBER: _ClassVar[int]
    id: str
    tenant_id: str
    seller_id: str
    title: str
    description: str
    listing_type: str
    price_type: str
    price_amount: int
    metadata_json: str
    sku: str
    def __init__(self, id: _Optional[str] = ..., tenant_id: _Optional[str] = ..., seller_id: _Optional[str] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., listing_type: _Optional[str] = ..., price_type: _Optional[str] = ..., price_amount: _Optional[int] = ..., metadata_json: _Optional[str] = ..., sku: _Optional[str] = ...) -> None: ...

class TokenUsageWire(_message.Message):
    __slots__ = ("user_id", "tenant_id", "model", "input_tokens", "output_tokens", "cost_usd", "timestamp")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    INPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    COST_USD_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    tenant_id: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: str
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, user_id: _Optional[str] = ..., tenant_id: _Optional[str] = ..., model: _Optional[str] = ..., input_tokens: _Optional[int] = ..., output_tokens: _Optional[int] = ..., cost_usd: _Optional[str] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class UserWire(_message.Message):
    __slots__ = ("id", "email", "display_name", "tenant_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    email: str
    display_name: str
    tenant_id: str
    def __init__(self, id: _Optional[str] = ..., email: _Optional[str] = ..., display_name: _Optional[str] = ..., tenant_id: _Optional[str] = ...) -> None: ...
