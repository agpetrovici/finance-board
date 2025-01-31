import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Dict, Optional


@dataclass
class Card:
    id: str
    last_four: str
    brand: Optional[str] = None
    currency: Optional[str] = None


@dataclass
class Account:
    id: str
    type: str


@dataclass
class LocalisedDescriptionParam:
    key: str
    value: str


@dataclass
class LocalisedDescription:
    key: str
    params: List[LocalisedDescriptionParam]


@dataclass
class Merchant:
    id: str
    merchant_id: str
    scheme: str
    name: str
    mcc: str
    category: str
    city: str
    country: str
    address: str
    state: str
    logo: str
    brand_id: str
    can_be_blocked: bool


@dataclass
class RevolutTransaction:
    id: str
    leg_id: str
    group_key: str
    type: str
    state: str
    started_date: datetime
    updated_date: datetime
    completed_date: datetime
    created_date: datetime
    currency: str
    amount: float
    fee: float
    balance: float
    description: str
    tag: str
    category: str
    account: Account
    suggestions: List[str]
    comment: Optional[str] = None
    merchant: Optional[Merchant] = None
    topup_method: Optional[str] = None
    topup_source: Optional[str] = None
    card: Optional[Card] = None
    localised_description: Optional[LocalisedDescription] = None

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "RevolutTransaction":
        # Convert timestamps to datetime objects
        date_fields = ["startedDate", "updatedDate", "completedDate", "createdDate"]
        for field in date_fields:
            if field in data:
                data[field] = datetime.fromtimestamp(data[field] / 1000)  # Convert milliseconds to seconds

        # Create nested objects
        account = Account(id=data["account"]["id"], type=data["account"]["type"])

        card = None
        if "card" in data:
            card = Card(
                id=data["card"]["id"],
                last_four=data["card"]["lastFour"],
                brand=data["card"].get("brand"),
                currency=data["card"].get("currency"),
            )

        localised_description = None
        if "localisedDescription" in data:
            params = [LocalisedDescriptionParam(key=param["key"], value=param["value"]) for param in data["localisedDescription"]["params"]]
            localised_description = LocalisedDescription(key=data["localisedDescription"]["key"], params=params)

        # Create the main transaction object
        merchant = None
        if "merchant" in data:
            merchant = Merchant(
                id=data["merchant"]["id"],
                merchant_id=data["merchant"]["merchantId"],
                scheme=data["merchant"]["scheme"],
                name=data["merchant"]["name"],
                mcc=data["merchant"]["mcc"],
                category=data["merchant"]["category"],
                city=data["merchant"]["city"],
                country=data["merchant"]["country"],
                address=data["merchant"]["address"],
                state=data["merchant"]["state"],
                logo=data["merchant"]["logo"],
                brand_id=data["merchant"]["brandId"],
                can_be_blocked=data["merchant"]["canBeBlocked"],
            )

        return cls(
            id=data["id"],
            leg_id=data["legId"],
            group_key=data["groupKey"],
            type=data["type"],
            state=data["state"],
            started_date=data["startedDate"],
            updated_date=data["updatedDate"],
            completed_date=data["completedDate"],
            created_date=data["createdDate"],
            currency=data["currency"],
            amount=data["amount"] / 100,
            fee=data["fee"] / 100,
            balance=data["balance"] / 100,
            description=data["description"],
            tag=data["tag"],
            category=data["category"],
            account=account,
            suggestions=data["suggestions"],
            comment=data.get("comment"),
            merchant=merchant,
            topup_method=data.get("topupMethod"),
            topup_source=data.get("topupSource"),
            card=card,
            localised_description=localised_description,
        )

    @classmethod
    def from_dict(cls, data: List[Dict[str, Any]]) -> List["RevolutTransaction"]:
        return [cls._from_dict(x) for x in data[::-1]]

    @classmethod
    def from_json(cls, data: str) -> List["RevolutTransaction"]:
        return [cls._from_dict(x) for x in json.loads(data)[::-1]]
