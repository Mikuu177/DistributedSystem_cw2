import json
import os

import pyodbc
from azure.identity import DeviceCodeCredential


def main():
    cfg = json.load(open("local.settings.json", encoding="utf-8"))
    os.environ.update(cfg["Values"])
    conn_str = os.environ["SQL_CONNECTION_STRING"]

    def prompt_callback(verification_uri, user_code, expires_on):
        print(
            f"To sign in, open {verification_uri} and enter the code {user_code}. "
            f"Code expires at {expires_on}."
        )

    credential = DeviceCodeCredential(
        client_id="04b07795-8ddb-461a-bbee-02f9e1bf7b46",
        prompt_callback=prompt_callback,
    )
    token = credential.get_token("https://database.windows.net/.default")
    token_bytes = token.token.encode("utf-16-le")

    conn = pyodbc.connect(conn_str, attrs_before={1256: token_bytes})
    with conn.cursor() as cur:
        cur.execute("SELECT TOP 1 name FROM sys.tables")
        print("Sample row:", cur.fetchone())
    print("Connected OK")


if __name__ == "__main__":
    main()
