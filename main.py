import base64
import json
import random
import time
import uuid
from typing import List

import requests
import xmltodict
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.Padding import pad
from pywidevine import Device, Cdm, PSSH
from pywidevine import Key


class InkryptVideos:
    def __init__(self, device: Device, video_id: str, otp: str):
        self.device = device
        self.video_id = video_id
        self.otp = otp

        self._session = requests.Session()

        self._APP_VER = "3.0.63"
        self._VER = "1.0.63"
        self._USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0"

    @staticmethod
    def b64enc(s):
        return base64.b64encode(s.encode()).decode()

    @staticmethod
    def _ensure_list(element: dict | list) -> list:
        if isinstance(element, dict):
            return [element]
        return element

    @staticmethod
    def extract_pssh(s: str) -> str:
        dict_manifest = xmltodict.parse(s)
        for period in InkryptVideos._ensure_list(dict_manifest["MPD"]["Period"]):
            for ad_set in InkryptVideos._ensure_list(period["AdaptationSet"]):
                for content_protection in InkryptVideos._ensure_list(ad_set.get("ContentProtection", [])):
                    if content_protection.get("@schemeIdUri", "").lower() == "urn:uuid:edef8ba9-79d6-4ace-a3c8-27dcd51d21ed":
                        return content_protection.get("cenc:pssh")
                for representation in ad_set.get("Representation", []):
                    for content_protection in InkryptVideos._ensure_list(representation.get("ContentProtection")):
                        if content_protection.get("@schemeIdUri", "").lower() == "urn:uuid:edef8ba9-79d6-4ace-a3c8-27dcd51d21ed":
                            return content_protection["cenc:pssh"]["#text"]

    def get_manifest_url(self) -> str:
        response = self._session.get(
            url=f'https://api.inkryptvideos.com/api/s1/v_info/{self.video_id}',
            headers={
                'user-agent': self._USER_AGENT,
                'x-otp': self.otp,
                'x-version': '2.1.127',
            }
        )

        response.raise_for_status()
        response_json = response.json()

        data = response_json["data"]

        return f"https://{data["storage_hostname"]}/{data["dash_manifest"]}"

    def get_keys(self, pssh: PSSH) -> List[Key]:
        cdm = Cdm.from_device(self.device)

        session_id = cdm.open()
        challenge = cdm.get_license_challenge(session_id, pssh)

        # generate some fake values
        app_info = json.dumps({
            "a": get_random_bytes(8).hex(),  # android ID
            "b": str(uuid.uuid4()),  # app ID
            "c": str(int((time.time() - random.randrange(60 * 10, 3600 * 24 * 10)) * 1000))  # installation time
        }, separators=(',', ':'))

        config = json.dumps({
            "a": self.b64enc("com.inkryptvideos.ink_player"),
            "c": base64.b64encode(challenge).decode(),
            "d": self.b64enc(self.b64enc(app_info)),
            "sv": self.b64enc(self.b64enc(self._APP_VER)),
            "v": self.b64enc(self._VER)
        }, separators=(',', ':'))

        cipher = AES.new(
            key=self.otp[:32].encode(),
            mode=AES.MODE_CBC,
            iv=self.video_id[:16].encode()
        )
        serialized_config = self.b64enc(self.b64enc(config))
        encrypted_config = base64.b64encode(cipher.encrypt(pad(serialized_config.encode(), AES.block_size))).decode()

        token = json.dumps({
            "c": self.b64enc(self.b64enc(encrypted_config)),
            "v": self.video_id
        }, separators=(',', ':'))

        payload = json.dumps({
            "token": self.b64enc(token)
        }, separators=(',', ':'))

        response = self._session.post(
            url="https://license.inkryptvideos.com/api/v1/android/license",
            headers={
                "User-Agent": "okhttp/4.12.0",
                "x-otp": self.otp,
                "x-version": self._APP_VER,
                "Content-Type": "application/json"
            },
            data=payload
        )

        response.raise_for_status()
        response_json = response.json()

        cdm.parse_license(session_id, response_json["l"])

        keys = cdm.get_keys(session_id, type_="CONTENT")

        cdm.close(session_id)

        return keys



if __name__ == '__main__':
    # query your site's endpoint to get the video ID and OTP
    response = requests.get(
        url='https://...',
        headers={
            'user-agent': "...",
            'authorization': '...',
            'x-xsrf-token': '...',
        }
    )

    response.raise_for_status()
    response_json = response.json()

    # initialize class with Widevine Device, video ID and OTP
    ink = InkryptVideos(
        device=Device.load("DEVICE.wvd"),
        video_id="<get from response_json>",
        otp="<get from response_json>"
    )

    manifest_url = ink.get_manifest_url()
    print(manifest_url)

    manifest = requests.get(manifest_url)
    manifest.raise_for_status()

    pssh = PSSH(InkryptVideos.extract_pssh(manifest.text))
    keys = ink.get_keys(pssh)

    for key in keys:
        print(f"[{key.type}] {key.kid.hex}:{key.key.hex()}")



