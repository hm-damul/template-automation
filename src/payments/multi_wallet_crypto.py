"""Advanced Crypto Payment System - Multi-Wallet Network Support"""
import os
import json
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CryptoNetwork(Enum):
    """암호화페 네트워크"""
    ETHEREUM = "ethereum"
    SOLANA = "solana"
    BITCOIN = "bitcoin"
    BSC = "bsc"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    AVALANCHE = "avalanche"


class CryptoCurrency(Enum):
    """지원 암호화페"""
    # Ethereum/ERC-20
    ETH = {"network": CryptoNetwork.ETHEREUM, "symbol": "ETH", "name": "Ethereum"}
    USDC_ETH = {"network": CryptoNetwork.ETHEREUM, "symbol": "USDC", "name": "USD Coin (ETH)"}
    USDT_ETH = {"network": CryptoNetwork.ETHEREUM, "symbol": "USDT", "name": "Tether (ETH)"}
    
    # Solana
    SOL = {"network": CryptoNetwork.SOLANA, "symbol": "SOL", "name": "Solana"}
    USDC_SOL = {"network": CryptoNetwork.SOLANA, "symbol": "USDC", "name": "USD Coin (SOL)"}
    
    # Bitcoin
    BTC = {"network": CryptoNetwork.BITCOIN, "symbol": "BTC", "name": "Bitcoin"}
    
    # BSC
    BNB = {"network": CryptoNetwork.BSC, "symbol": "BNB", "name": "BNB"}
    USDT_BSC = {"network": CryptoNetwork.BSC, "symbol": "USDT", "name": "Tether (BSC)"}
    
    # Polygon
    MATIC = {"network": CryptoNetwork.POLYGON, "symbol": "MATIC", "name": "Polygon"}
    USDC_POL = {"network": CryptoNetwork.POLYGON, "symbol": "USDC", "name": "USD Coin (POL)"}


@dataclass
class WalletConfig:
    """지갑 설정"""
    name: str
    network: CryptoNetwork
    address: str
    qr_code: str = ""
    memo_required: bool = False
    memo: str = ""


# 플랫폼별 지원 암호화페 매핑
PLATFORM_CRYPTO_SUPPORT = {
    "stripe": [
        CryptoCurrency.USDC_ETH.value["symbol"],
        CryptoCurrency.USDT_ETH.value["symbol"],
        CryptoCurrency.ETH.value["symbol"],
        CryptoCurrency.USDC_SOL.value["symbol"]
    ],
    "coinbase_commerce": [
        CryptoCurrency.BTC.value["symbol"],
        CryptoCurrency.ETH.value["symbol"],
        CryptoCurrency.USDC_ETH.value["symbol"],
        CryptoCurrency.LTC.value["symbol"] if hasattr(CryptoCurrency, 'LTC') else None
    ],
    "bitpay": [
        CryptoCurrency.BTC.value["symbol"],
        CryptoCurrency.ETH.value["symbol"],
        CryptoCurrency.USDC_ETH.value["symbol"],
        CryptoCurrency.DOGE.value["symbol"] if hasattr(CryptoCurrency, 'DOGE') else None
    ],
    "manual_wallet": [  # 직접 지갑 송금
        CryptoCurrency.ETH.value["symbol"],
        CryptoCurrency.USDC_ETH.value["symbol"],
        CryptoCurrency.USDT_ETH.value["symbol"],
        CryptoCurrency.SOL.value["symbol"],
        CryptoCurrency.USDC_SOL.value["symbol"],
        CryptoCurrency.BTC.value["symbol"]
    ]
}


class MultiWalletPaymentSystem:
    """다중 지갑 암호화페 결제 시스템"""
    
    def __init__(self):
        self.wallets = self._load_wallet_configs()
        self.exchange_rates = {}
    
    def _load_wallet_configs(self) -> Dict[str, WalletConfig]:
        """지갑 설정 로드"""
        wallets = {}
        
        # MetaMask ETH 주소
        if os.getenv("METAMASK_ETH_ADDRESS"):
            wallets["ETH"] = WalletConfig(
                name="MetaMask (ETH)",
                network=CryptoNetwork.ETHEREUM,
                address=os.getenv("METAMASK_ETH_ADDRESS")
            )
        
        # MetaMask BTC 주소  
        if os.getenv("METAMASK_BTC_ADDRESS"):
            wallets["BTC"] = WalletConfig(
                name="MetaMask (BTC)",
                network=CryptoNetwork.BITCOIN,
                address=os.getenv("METAMASK_BTC_ADDRESS")
            )
        
        # Trust Wallet ETH 주소
        if os.getenv("TRUSTWALLET_ETH_ADDRESS"):
            wallets["TRUST_ETH"] = WalletConfig(
                name="Trust Wallet (ETH)",
                network=CryptoNetwork.ETHEREUM,
                address=os.getenv("TRUSTWALLET_ETH_ADDRESS")
            )
        
        # Trust Wallet SOL 주소
        if os.getenv("TRUSTWALLET_SOL_ADDRESS"):
            wallets["TRUST_SOL"] = WalletConfig(
                name="Trust Wallet (SOL)",
                network=CryptoNetwork.SOLANA,
                address=os.getenv("TRUSTWALLET_SOL_ADDRESS")
            )
        
        # Phantom SOL 주소
        if os.getenv("PHANTOM_SOL_ADDRESS"):
            wallets["PHANTOM_SOL"] = WalletConfig(
                name="Phantom (SOL)",
                network=CryptoNetwork.SOLANA,
                address=os.getenv("PHANTOM_SOL_ADDRESS")
            )
        
        # BSC 주소 (Trust Wallet으로 대표)
        if os.getenv("TRUSTWALLET_BSC_ADDRESS"):
            wallets["BSC"] = WalletConfig(
                name="Trust Wallet (BSC)",
                network=CryptoNetwork.BSC,
                address=os.getenv("TRUSTWALLET_BSC_ADDRESS")
            )
        
        return wallets
    
    def get_supported_crypto_list(self) -> List[Dict]:
        """지원되는 암호화페 목록 반환"""
        supported = []
        
        for crypto in CryptoCurrency:
            wallet = self._get_wallet_for_crypto(crypto)
            if wallet:
                supported.append({
                    "symbol": crypto.value["symbol"],
                    "name": crypto.value["name"],
                    "network": crypto.value["network"].value,
                    "wallet_name": wallet.name,
                    "wallet_address": wallet.address
                })
        
        return supported
    
    def _get_wallet_for_crypto(self, crypto: CryptoCurrency) -> Optional[WalletConfig]:
        """암호화페에 맞는 지갑 반환"""
        crypto_info = crypto.value
        network = crypto_info["network"]
        
        # 네트워크별 우선순위 지갑 선택
        priority_wallets = {
            CryptoNetwork.ETHEREUM: ["ETH", "TRUST_ETH"],
            CryptoNetwork.SOLANA: ["PHANTOM_SOL", "TRUST_SOL"],
            CryptoNetwork.BITCOIN: ["BTC"],
            CryptoNetwork.BSC: ["BSC"],
            CryptoNetwork.POLYGON: ["TRUST_ETH"],  # Polygon은 ETH 지갑 사용 가능
            CryptoNetwork.ARBITRUM: ["ETH"],  # Arbitrum은 ETH 지갑 사용 가능
            CryptoNetwork.OPTIMISM: ["ETH"],  # Optimism은 ETH 지갑 사용 가능
        }
        
        priority = priority_wallets.get(network, [])
        
        for wallet_key in priority:
            if wallet_key in self.wallets:
                return self.wallets[wallet_key]
        
        return None
    
    def create_payment_request(self, amount_usd: float, crypto_symbol: str, order_id: str) -> Dict:
        """결제 요청 생성"""
        # 암호화페 찾기
        crypto = self._find_crypto_by_symbol(crypto_symbol)
        if not crypto:
            return {"success": False, "error": f"Unsupported crypto: {crypto_symbol}"}
        
        # 지갑 찾기
        wallet = self._get_wallet_for_crypto(crypto)
        if not wallet:
            return {"success": False, "error": f"No wallet configured for {crypto.value['name']}"}
        
        # 환율 조회
        exchange_rate = self._get_exchange_rate(crypto.value["symbol"])
        crypto_amount = round(amount_usd / exchange_rate, 6)
        
        payment_data = {
            "order_id": order_id,
            "crypto": crypto.value["symbol"],
            "crypto_name": crypto.value["name"],
            "network": wallet.network.value,
            "crypto_amount": crypto_amount,
            "usd_amount": amount_usd,
            "exchange_rate": exchange_rate,
            "wallet_name": wallet.name,
            "wallet_address": wallet.address,
            "qr_code": self._generate_qr_code(wallet.address, crypto_amount, crypto.value["symbol"]),
            "memo_required": wallet.memo_required,
            "memo": wallet.memo if wallet.memo_required else "",
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "instructions": self._generate_payment_instructions(wallet, crypto, crypto_amount)
        }
        
        logger.info(f"Payment request created: {payment_data}")
        
        return {
            "success": True,
            "payment_data": payment_data
        }
    
    def _find_crypto_by_symbol(self, symbol: str) -> Optional[CryptoCurrency]:
        """심볼로 암호화페 찾기"""
        symbol_upper = symbol.upper()
        
        for crypto in CryptoCurrency:
            if crypto.value["symbol"] == symbol_upper:
                return crypto
        
        # USDT/USDC는 네트워크 확인 필요
        if symbol_upper in ["USDT", "USDC"]:
            # 기본적으로 ETH 네트워크 사용
            if symbol_upper == "USDC":
                return CryptoCurrency.USDC_ETH
            else:
                return CryptoCurrency.USDT_ETH
        
        return None
    
    def _get_exchange_rate(self, crypto_symbol: str) -> float:
        """환율 조회"""
        try:
            response = requests.get(
                f"https://min-api.cryptocompare.com/data/price",
                params={"fsym": crypto_symbol, "tsyms": "USD"}
            )
            data = response.json()
            return data.get("USD", 0)
        except Exception as e:
            logger.error(f"Error getting exchange rate for {crypto_symbol}: {e}")
            return 0
    
    def _generate_qr_code(self, address: str, amount: float, crypto: str) -> str:
        """QR 코드 생성 (암호화페 URI 스킴)"""
        # Crypto URI 스킴 생성
        if crypto in ["BTC"]:
            return f"bitcoin:{address}?amount={amount}"
        elif crypto in ["ETH", "USDC", "USDT"]:
            return f"ethereum:{address}?value={int(amount * 1e18)}"
        elif crypto in ["SOL", "USDC_SOL"]:
            return f"solana:{address}?amount={amount}"
        else:
            return address
    
    def _generate_payment_instructions(self, wallet: WalletConfig, crypto: CryptoCurrency, amount: float) -> str:
        """결제 안내 생성"""
        network = wallet.network.value
        crypto_info = crypto.value
        
        instructions = f"""
**{crypto_info['name']} 결제 안내**

1. **암호화페**: {crypto_info['symbol']}
2. **네트워크**: {network.upper()}
3. **지갑**: {wallet.name}

**송금 주소:**
```{wallet.address}```

**송금 금액**: {amount} {crypto_info['symbol']}

"""
        
        if wallet.memo_required:
            instructions += f"**메모 (필수)**: `{wallet.memo}`\n"
        
        instructions += """
**주의사항**:
- 잘못된 네트워크로 전송 시 자금이 손실될 수 있습니다.
- 정확한 금액을 송금해 주세요.
- 네트워크 확인 후 10-30분 내 도착합니다.
"""
        
        return instructions
    
    def get_optimal_crypto_for_platform(self, platform: str) -> List[Dict]:
        """플랫폼별 최적 암호화페 반환"""
        if platform not in PLATFORM_CRYPTO_SUPPORT:
            platform = "manual_wallet"
        
        supported_symbols = PLATFORM_CRYPTO_SUPPORT[platform]
        optimal = []
        
        for symbol in supported_symbols:
            if symbol:  # None이 아닌 경우
                crypto = self._find_crypto_by_symbol(symbol)
                if crypto:
                    wallet = self._get_wallet_for_crypto(crypto)
                    if wallet:
                        exchange_rate = self._get_exchange_rate(symbol)
                        optimal.append({
                            "symbol": symbol,
                            "crypto_name": crypto.value["name"],
                            "network": crypto.value["network"].value,
                            "wallet_name": wallet.name,
                            "wallet_address": wallet.address,
                            "estimated_usd_per_1_unit": exchange_rate
                        })
        
        return optimal
    
    def check_payment_status(self, order_id: str, crypto_symbol: str, tx_hash: str = None) -> Dict:
        """결제 상태 확인"""
        # 실제로는 블록체인Explorer API 호출
        # 여기서는 시뮬레이션
        
        return {
            "order_id": order_id,
            "crypto": crypto_symbol,
            "status": "pending",  # pending, confirmed, failed
            "tx_hash": tx_hash,
            "network": "ethereum",
            "confirmations": 0,
            "message": "결제를 확인 중입니다..."
        }


class CryptoPaymentOptimizer:
    """암호화페 결제 최적화"""
    
    def __init__(self):
        self.payment_system = MultiWalletPaymentSystem()
    
    def get_best_payment_option(self, amount_usd: float, platform: str = "manual") -> Dict:
        """최적 결제 옵션 반환"""
        options = self.payment_system.get_optimal_crypto_for_platform(platform)
        
        if not options:
            return {
                "success": False,
                "error": "No payment options available",
                "action": "Setup wallet addresses in .env file"
            }
        
        # 최적 옵션 선택 (가장 낮은 네트워크 수수료 + 안정성)
        best_option = options[0]  # 기본적으로 첫 번째 옵션 (USDC-ETH)
        
        # USD 기반-stablecoin 우선 (가격 변동 위험 최소화)
        stablecoin_options = [opt for opt in options if "USDC" in opt["symbol"] or "USDT" in opt["symbol"]]
        
        if stablecoin_options:
            best_option = stablecoin_options[0]
        
        # 결제 요청 생성
        payment_result = self.payment_system.create_payment_request(
            amount_usd,
            best_option["symbol"],
            f"order_{datetime.now().timestamp()}"
        )
        
        if payment_result["success"]:
            return {
                "success": True,
                "recommended_crypto": best_option,
                "payment_details": payment_result["payment_data"],
                "alternatives": options[1:3] if len(options) > 1 else []  # 대안 2개
            }
        
        return payment_result
    
    def setup_wallet_guide(self) -> str:
        """지갑 설정 가이드"""
        guide = """
=== 암호화페 지갑 설정 가이드 ===

**1. MetaMask 설정 (.env 파일 편집)**

# ETH 주소 (0x로 시작)
METAMASK_ETH_ADDRESS=0x1234...

# BTC 주소 (bc1로 시작)  
METAMASK_BTC_ADDRESS=bc1abcd...

**2. Trust Wallet 설정**

# ETH 주소
TRUSTWALLET_ETH_ADDRESS=0x5678...

# SOL 주소
TRUSTWALLET_SOL_ADDRESS=ABCdef...

# BSC 주소
TRUSTWALLET_BSC_ADDRESS=0x9abc...

**3. Phantom 설정**

# SOL 주소
PHANTOM_SOL_ADDRESS=Sol123...

**설정 후 재실행:**
python src/main.py test

=== 지원 암호화페 ===
- ETH (Ethereum)
- USDC (ETH, SOL)
- USDT (ETH, BSC)
- SOL (Solana)
- BTC (Bitcoin)
- BNB (BSC)
"""
        return guide


# Export
crypto_payment_system = MultiWalletPaymentSystem()
crypto_optimizer = CryptoPaymentOptimizer()
