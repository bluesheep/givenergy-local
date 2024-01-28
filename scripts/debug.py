#!/usr/bin/env python3

"""CLI tool for inverter debugging."""

import argparse
import asyncio
import json
import logging

from custom_components.givenergy_local.givenergy_modbus.client.client import Client
from custom_components.givenergy_local.givenergy_modbus.model.plant import Plant

logging.basicConfig(format="%(name)s %(levelname)s %(message)s", level=logging.INFO)


def main() -> None:
    """Main entry point of the CLI tool."""
    parser = argparse.ArgumentParser()
    parser.add_argument("inverter_host", help="Hostname or IP address of the inverter")
    parser.add_argument(
        "-b", "--batteries", type=int, default=0, help="Number of attached batteries"
    )
    args = parser.parse_args()

    asyncio.run(_perform_debug(args))


async def _perform_debug(args: argparse.Namespace) -> None:
    debugger = InverterDebugger(args.inverter_host, args.batteries)
    await debugger.full_refresh()
    await debugger.display_raw_registers()
    await debugger.display_decoded_data()


class InverterDebugger:
    """Provides debugging tools that read and display inverter data at various levels."""

    def __init__(self, host: str, num_batteries: int) -> None:
        """Initialize the inverter client and perform a full refresh"""
        self.num_batteries = num_batteries
        self.plant = Plant(number_batteries=num_batteries)
        self.client = Client(host, 8899)

    async def full_refresh(self) -> Plant:
        """Performs a full refresh of inverter and battery data."""
        logging.info("Performing full refresh...")
        return await self.client.refresh_plant(full_refresh=True)

    async def display_raw_registers(self) -> None:
        """
        Prints raw register data to stdout.

        This avoids decoding steps that can cause issues on unfamiliar hardware.
        """
        logging.info("Dumping inverter registers...")
        print(json.dumps(self.plant.inverter_rc, indent=2))

        for battery_id in range(self.num_batteries):
            logging.info("Dumping battery %s registers...", battery_id)
            print(json.dumps(self.plant.batteries_rcs[battery_id], indent=2))

    async def display_decoded_data(self) -> None:
        """Decodes inverter and battery data, pretty printing it to stdout."""
        logging.info("Decoding and printing inverter data...")
        print(self.plant.inverter.json(indent=2))

        for battery_id in range(self.num_batteries):
            logging.info("Decoding and printing battery %s data...", battery_id)
            print(self.plant.batteries[battery_id].json(indent=2))


if __name__ == "__main__":
    main()
