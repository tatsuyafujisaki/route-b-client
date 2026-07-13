import logging
import os
import sys
import time

import momonga


def main() -> None:
    env_vars = {k: os.getenv(k) for k in ("ROUTE_B_ID", "ROUTE_B_PASSWORD", "ROUTE_B_DEVICE")}
    if missing := [k for k, v in env_vars.items() if not v]:
        sys.exit(f"Error: Missing or empty environment variables: {', '.join(missing)}")

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    for logger in (momonga.logger, momonga.session_manager_logger, momonga.sk_wrapper_logger):
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    while True:
        try:
            with momonga.Momonga(
                env_vars["ROUTE_B_ID"],
                env_vars["ROUTE_B_PASSWORD"],
                env_vars["ROUTE_B_DEVICE"]
            ) as mo:
                print("Successfully connected to the smart meter.", flush=True)
                print(f"Supported EPCs to get values: {mo.get_properties_to_get_values()}", flush=True)

                while True:
                    print(f"Instantaneous Power: {mo.get_instantaneous_power():.1f}W", flush=True)
                    try:
                        print(f"Historical Cumulative Energy 1: {mo.get_historical_cumulative_energy_1()}", flush=True)
                    except momonga.MomongaResponseNotPossible:
                        print("Historical Cumulative Energy 1 is not supported.", flush=True)

                    time.sleep(60)

        except (
            momonga.MomongaSkScanFailure,
            momonga.MomongaSkJoinFailure,
            momonga.MomongaNeedToReopen,
        ) as e:
            print(f"{type(e).__name__}: {e}\nRetrying in 10 seconds...", file=sys.stderr, flush=True)
            time.sleep(10)
        except KeyboardInterrupt:
            print("Terminating...", flush=True)
            break
        except Exception as e:
            sys.exit(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
