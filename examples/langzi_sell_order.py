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


            sellOrder(client, random_key, sell_float)

            getVolume(proxy_wallet)


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
                    token_id="45714870634090908403813747458214625542376052548606303175331201110938821302832",
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

main()
