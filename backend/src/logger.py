from datetime import datetime


def log_event(event, data=None):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    print("\n" + "=" * 50)
    print(f"[{timestamp}] {event}")

    if data:

        for key, value in data.items():

            print(f"{key}: {value}")

    print("=" * 50)