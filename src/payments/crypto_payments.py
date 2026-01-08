"""Payment Module - Crypto Payment Automation"""
import os
import json
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class CryptoPaymentSystem:
    """암호화페 결제 시스템 - Stripe Crypto + WalletConnect"""
    
    def __init__(self):
        self.stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
        self.wallet_address = os.getenv("WALLET_ADDRESS")
        self.crypto_apis_key = os.getenv("CRYPTO_APIS_KEY")
        
    def create_crypto_payment_intent(self, amount_usd: float, metadata: Dict = None) -> Dict:
        """Stripe Crypto 결제 생성"""
        if not self.stripe_secret_key:
            return {"success": False, "error": "Stripe key not configured"}
        
        try:
            import stripe
            stripe.api_key = self.stripe_secret_key
            
            intent = stripe.PaymentIntent.create(
                amount=int(amount_usd * 100),  # cents
                currency="usd",
                payment_method_types=["crypto"],
                metadata=metadata or {}
            )
            
            return {
                "success": True,
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "crypto_url": f"https://crypto.stripe.com/pay/{intent.id}"
            }
            
        except Exception as e:
            logger.error(f"Stripe crypto payment error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_crypto_exchange_rate(self, crypto: str = "ETH", currency: str = "USD") -> float:
        """암호화페 환율 조회"""
        try:
            response = requests.get(
                f"https://min-api.cryptocompare.com/data/price",
                params={"fsym": crypto, "tsyms": currency}
            )
            data = response.json()
            return data.get(currency, 0)
            
        except Exception as e:
            logger.error(f"Error getting exchange rate: {e}")
            return 0
    
    def create_wallet_payment_request(self, amount_usd: float, order_id: str, crypto: str = "USDC") -> Dict:
        """지갑 결제 요청 생성"""
        exchange_rate = self.get_crypto_exchange_rate(crypto)
        crypto_amount = Decimal(str(amount_usd)) / Decimal(str(exchange_rate))
        
        payment_data = {
            "order_id": order_id,
            "crypto": crypto,
            "crypto_amount": round(float(crypto_amount), 6),
            "usd_amount": amount_usd,
            "exchange_rate": exchange_rate,
            "wallet_address": self.wallet_address,
            "network": "ethereum" if crypto in ["USDC", "USDT", "ETH"] else "solana",
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"Wallet payment request created: {payment_data}")
        
        return {
            "success": True,
            "payment_data": payment_data,
            "payment_url": f"crypto:{self.wallet_address}?amount={payment_data['crypto_amount']}"
        }
    
    def check_transaction_status(self, tx_hash: str, network: str = "ethereum") -> Dict:
        """트랜잭션 상태 확인"""
        try:
            if network == "ethereum":
                # Etherscan API 활용
                response = requests.get(
                    f"https://api.etherscan.io/api",
                    params={
                        "module": "proxy",
                        "action": "eth_getTransactionReceipt",
                        "txhash": tx_hash,
                        "apikey": os.getenv("ETHERSCAN_API_KEY", "")
                    }
                )
                
                if response.json().get("result"):
                    return {
                        "status": "confirmed",
                        "tx_hash": tx_hash,
                        "network": network
                    }
                else:
                    return {
                        "status": "pending",
                        "tx_hash": tx_hash,
                        "network": network
                    }
            
            return {"status": "unknown", "tx_hash": tx_hash}
            
        except Exception as e:
            logger.error(f"Error checking transaction: {e}")
            return {"status": "error", "error": str(e)}
    
    def process_webhook_payment(self, webhook_data: Dict) -> Dict:
        """웹훅을 통한 결제 처리"""
        event_type = webhook_data.get("type")
        data = webhook_data.get("data", {}).get("object", {})
        
        if event_type == "payment_intent.succeeded":
            return {
                "action": "fulfill_order",
                "order_id": data.get("metadata", {}).get("order_id"),
                "amount": data.get("amount") / 100,
                "currency": data.get("currency"),
                "payment_method": "crypto"
            }
        
        elif event_type == "payment_intent.payment_failed":
            return {
                "action": "notify_failure",
                "order_id": data.get("metadata", {}).get("order_id"),
                "error": data.get("last_payment_error", {}).get("message")
            }
        
        return {"action": "ignore", "event_type": event_type}


class AccountingSystem:
    """회계 시스템 - 자동 원장 업데이트"""
    
    def __init__(self):
        self.transactions = []
        self.ledger = {}
        
    def record_transaction(self, transaction: Dict):
        """거래 기록"""
        self.transactions.append({
            **transaction,
            "recorded_at": datetime.now().isoformat()
        })
        
        # 원장에 업데이트
        self._update_ledger(transaction)
        
    def _update_ledger(self, transaction: Dict):
        """원장 업데이트"""
        account = transaction.get("account", "revenue")
        if account not in self.ledger:
            self.ledger[account] = {
                "debits": 0,
                "credits": 0,
                "balance": 0
            }
        
        if transaction.get("type") == "credit":
            self.ledger[account]["credits"] += transaction.get("amount", 0)
            self.ledger[account]["balance"] += transaction.get("amount", 0)
        else:
            self.ledger[account]["debits"] += transaction.get("amount", 0)
            self.ledger[account]["balance"] -= transaction.get("amount", 0)
    
    def get_financial_summary(self) -> Dict:
        """재무 요약"""
        total_revenue = sum(
            t.get("amount", 0) 
            for t in self.transactions 
            if t.get("type") == "credit"
        )
        
        return {
            "total_revenue": total_revenue,
            "transaction_count": len(self.transactions),
            "ledger": self.ledger,
            "period": {
                "start": self.transactions[0]["recorded_at"] if self.transactions else None,
                "end": self.transactions[-1]["recorded_at"] if self.transactions else None
            }
        }
    
    def generate_tax_report(self, year: int = None) -> Dict:
        """세금 보고서 생성"""
        if year is None:
            year = datetime.now().year
        
        year_transactions = [
            t for t in self.transactions
            if t.get("recorded_at", "").startswith(str(year))
        ]
        
        total_income = sum(
            t.get("amount", 0)
            for t in year_transactions
            if t.get("type") == "credit"
        )
        
        return {
            "tax_year": year,
            "total_income": total_income,
            "transaction_count": len(year_transactions),
            "currency": "USD",
            "generated_at": datetime.now().isoformat(),
            "note": "For tax purposes. Consult a professional accountant."
        }


class PaymentAutomation:
    """결제 자동화 오케스트레이터"""
    
    def __init__(self):
        self.crypto = CryptoPaymentSystem()
        self.accounting = AccountingSystem()
        
    def process_payment(self, order_data: Dict) -> Dict:
        """결제 처리 자동화"""
        amount_usd = order_data.get("amount_usd", 0)
        order_id = order_data.get("order_id", str(datetime.now().timestamp()))
        
        # Stripe Crypto 결제 생성
        stripe_result = self.crypto.create_crypto_payment_intent(
            amount_usd, 
            {"order_id": order_id}
        )
        
        if stripe_result.get("success"):
            return {
                "success": True,
                "payment_type": "stripe_crypto",
                "payment_url": stripe_result["crypto_url"],
                "order_id": order_id
            }
        
        # 대안: 지갑 결제
        wallet_result = self.crypto.create_wallet_payment_request(
            amount_usd, 
            order_id
        )
        
        return {
            "success": True,
            "payment_type": "wallet",
            "payment_data": wallet_result["payment_data"],
            "order_id": order_id
        }
    
    def fulfill_order(self, order_id: str, payment_data: Dict):
        """주문 이행"""
        # 회계 기록
        self.accounting.record_transaction({
            "type": "credit",
            "account": "revenue",
            "amount": payment_data.get("amount", 0),
            "order_id": order_id,
            "description": f"Template sale - {order_id}"
        })
        
        logger.info(f"Order fulfilled: {order_id}")
        
        return {"success": True, "order_id": order_id}


# Export
payment_automation = PaymentAutomation()
accounting_system = AccountingSystem()
