#!/usr/bin/env python3
"""Deliver a message to WeChat via iLink Bot API (v2.4.3 protocol)."""

import urllib.request
import urllib.error
import json
import sys
import os
import random
import base64
import uuid

BASE_URL = "https://ilinkai.weixin.qq.com"
BOT_TOKEN = "f66dad4d7452@im.bot:060000bfb398af5bdda4928d541bcdf6a276fc"
TARGET_USER = "o9cq807vi7A2XVfcXvH8n3pT48Bs@im.wechat"
ENDPOINT = "ilink/bot/sendmessage"
APP_VERSION = "0x00020403"  # 2.4.3 encoded


def random_wechat_uin():
    uin = random.randint(1, 0xFFFFFFFF)
    return base64.b64encode(str(uin).encode()).decode()


def generate_client_id():
    return f"openclaw-weixin-{uuid.uuid4()}"


def read_message():
    if len(sys.argv) >= 3 and sys.argv[1] == "--file":
        path = sys.argv[2]
        if not os.path.exists(path):
            print(f"File not found: {path}", file=sys.stderr)
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    print("No message provided. Use --file <path> or pipe to stdin.", file=sys.stderr)
    sys.exit(1)


def send_message(text):
    url = f"{BASE_URL}/{ENDPOINT}"
    headers = {
        "Content-Type": "application/json",
        "AuthorizationType": "ilink_bot_token",
        "Authorization": f"Bearer {BOT_TOKEN}",
        "X-WECHAT-UIN": random_wechat_uin(),
        "iLink-App-Id": "bot",
        "iLink-App-ClientVersion": APP_VERSION,
    }
    body = {
        "msg": {
            "from_user_id": "",
            "to_user_id": TARGET_USER,
            "client_id": generate_client_id(),
            "message_type": 2,   # BOT
            "message_state": 2,  # FINISH
            "item_list": [
                {
                    "type": 1,  # TEXT
                    "text_item": {"text": text},
                }
            ],
        },
        "base_info": {
            "channel_version": "2.4.3",
            "bot_agent": "OpenClaw",
        },
    }

    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            result = resp.read().decode("utf-8")
            return resp.getcode(), result
    except urllib.error.HTTPError as e:
        body_text = ""
        try:
            body_text = e.read().decode("utf-8")
        except Exception:
            pass
        return e.code, body_text
    except Exception as e:
        return None, str(e)


def main():
    message = read_message()
    if len(message) > 4000:
        message = message[:4000] + "\n\n... (truncated)"

    code, resp = send_message(message)
    if code == 200:
        print(f"OK: {resp[:200]}")
    else:
        print(f"Delivery failed: HTTP {code} - {resp[:300]}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
