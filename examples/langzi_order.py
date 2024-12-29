import os
import time

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs, PartialCreateOrderOptions, OrderType, BalanceAllowanceParams, \
    AssetType, BookParams
from dotenv import load_dotenv
from py_clob_client.constants import POLYGON

from py_clob_client.order_builder.constants import BUY
from py_clob_client.order_builder.constants import SELL
import random
import requests

load_dotenv()


def main():
    host = "https://clob.polymarket.com"
    # key = os.getenv("PK")
    # creds = ApiCreds(
    #     api_key=os.getenv("CLOB_API_KEY"),
    #     api_secret=os.getenv("CLOB_SECRET"),
    #     api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    # )

    # 打开txt文件并读取
    with open('langzidata.txt', 'r') as file:
        for line in file:
            try:
                trade(host, line)
            except Exception as e:
                print(f"trade发生异常: {e}")


def trade(host, line):
    # 去除每行的换行符，并按逗号分割
    key, proxy_wallet = line.strip().split(',')
    print(f"key: {key}, proxy_wallet: {proxy_wallet}")
    chain_id = POLYGON
    client = ClobClient(host, key=key, chain_id=chain_id)
    try:
        creds = client.derive_api_key()
    except Exception as e:
        print(f"derive_api_key发生异常: {e}")
        client.create_api_key()
        creds = client.derive_api_key()
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds, signature_type=2, funder=proxy_wallet)
    data = client.get_prices(
        params=[
            BookParams(
                token_id="45714870634090908403813747458214625542376052548606303175331201110938821302832",
                side="BUY",
            ),
            BookParams(
                token_id="45714870634090908403813747458214625542376052548606303175331201110938821302832",
                side="SELL",
            ),
        ]
    )
    # 随机选择一个key
    random_key = random.choice(list(data.keys()))
    # 获取该key对应的BUY和SELL值，并转换为浮点数
    sell_str = data[random_key]['BUY']
    buy_str = data[random_key]['SELL']
    buy_float = float(buy_str)
    sell_float = float(sell_str)
    # 打印结果
    print(f"Random key: {random_key}")
    print(f"BUY as float: {buy_float}")
    print(f"SELL as float: {sell_float}")
    for i in range(55):
        try:
            time.sleep(random.uniform(5, 10))

            print(f"proxy_wallet: {proxy_wallet} 这是第 {i + 1} 次循环")
            # USDC
            client.update_balance_allowance(
                params=BalanceAllowanceParams(asset_type=AssetType.COLLATERAL)
            )
            collateral = client.get_balance_allowance(
                params=BalanceAllowanceParams(asset_type=AssetType.COLLATERAL)
            )

            # buyOrder(buy_float, client, collateral, random_key)
            buyPercentOrder(buy_float, client, collateral, random_key)

            sellOrder(client, random_key, sell_float)

            getVolume(proxy_wallet)
        except Exception as e:
            print(f"循环发生异常: {e}")

def buyOrder(buy_float, client, collateral, random_key):
    random_size = random.randint(20, 30)
    try:
        if collateral and int(collateral['balance']) > 30000000:
            # Create and sign a limit order buying 100 YES tokens for 0.0005 each
            buy_order_args = OrderArgs(
                price=buy_float,
                size=random_size,
                side=BUY,
                token_id=random_key,
            )
            buy_signed_order = client.create_order(buy_order_args)
            buy_resp = client.post_order(buy_signed_order)
            print(buy_resp)
            print("buy Done!")
    except Exception as e:
        print(f"下单发生异常: {e}")


def sellOrder(client, random_key, sell_float):
    for attempt in range(3):

        time.sleep(random.uniform(5, 10))

        try:
            # USDC
            client.update_balance_allowance(
                params=BalanceAllowanceParams(
                    asset_type=AssetType.CONDITIONAL,
                    token_id=random_key,
                )
            )
            tokenBalance = client.get_balance_allowance(
                params=BalanceAllowanceParams(
                    asset_type=AssetType.CONDITIONAL,
                    token_id=random_key,
                )
            )



            if tokenBalance and int(tokenBalance['balance']) > 0:
                order_args = OrderArgs(
                    price=sell_float,
                    size=int(tokenBalance['balance']) / 1000000,
                    side=SELL,
                    token_id=random_key,
                )
                signed_order = client.create_order(order_args)
                resp = client.post_order(signed_order)
                print(resp)
                print("sell Done!")
            break
        except Exception as e:
            print(f"发生异常: {e}")

def getVolume(proxy_wallet):
    try:
        url = f"https://lb-api.polymarket.com/volume?window=all&limit=1&address={proxy_wallet}"

        # 发送GET请求
        response = requests.get(url)

        # 检查请求是否成功
        if response.status_code == 200:
            # 打印响应内容
            print("Response data:", response.json())
        else:
            print(f"Request failed with status code {response.status_code}")
    except Exception as e:
        print(f"获取交易量异常: {e}")


def buyPercentOrder(buy_float, client, collateral, random_key):
    random_size = random.randint(50, 80) / 100
    try:
        if collateral:
            balance = int(collateral['balance'])
            trade_amount = balance * random_size/1000000
            # Create and sign a limit order buying 100 YES tokens for 0.0005 each
            buy_order_args = OrderArgs(
                price=buy_float,
                size=trade_amount,
                side=BUY,
                token_id=random_key,
            )
            buy_signed_order = client.create_order(buy_order_args)
            buy_resp = client.post_order(buy_signed_order)
            print(buy_resp)
            print("buy Done!")
    except Exception as e:
        print(f"下单发生异常: {e}")

main()
