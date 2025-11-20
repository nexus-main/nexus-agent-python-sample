import csv
import glob
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, cast
from urllib.request import url2pathname

from nexus_extensibility import (CatalogRegistration, LogLevel,  # type: ignore
                                 NexusDataType, ReadDataHandler, ReadRequest,
                                 Representation, ResourceBuilder,
                                 ResourceCatalog, ResourceCatalogBuilder,
                                 SimpleDataSource)


@dataclass(frozen=True)
class CsvReaderSettings():
    dummy: str

class CsvReader(SimpleDataSource[CsvReaderSettings]):
    
    async def get_catalog_registrations(self, path: str) -> list[CatalogRegistration]:

        if path == "/":
            return [
                CatalogRegistration("/A/B/C", "Test catalog /A/B/C."),
                CatalogRegistration("/D/E/F", "Test catalog /D/E/F.")
            ]

        else:
            return []

    async def enrich_catalog(self, catalog: ResourceCatalog):

        if (catalog.id == "/A/B/C"):

            representation = Representation(NexusDataType.FLOAT64, timedelta(seconds=600))

            resource1 = ResourceBuilder("wind_speed") \
                .with_unit("m/s") \
                .with_groups(["group1"]) \
                .with_property("column", 1) \
                .add_representation(representation) \
                .build()

            representation = Representation(NexusDataType.FLOAT64, timedelta(seconds=600))

            resource2 = ResourceBuilder("wind_direction") \
                .with_unit("deg") \
                .with_groups(["group2"]) \
                .with_property("column", 2) \
                .add_representation(representation) \
                .build()

            catalog = ResourceCatalogBuilder("/A/B/C") \
                .with_property("a", "b") \
                .with_property("c", 1) \
                .add_resources([resource1, resource2]) \
                .build()

        elif (catalog.id == "/D/E/F"):

            # Empty catalog
            catalog = ResourceCatalogBuilder("/D/E/F") \
                .build()

        else:
            raise Exception("Unknown catalog identifier.")

        return catalog

    async def read(
        self, 
        begin: datetime,
        end: datetime,
        requests: list[ReadRequest], 
        read_data: ReadDataHandler,
        report_progress: Callable[[float], None]
    ) -> None:
        
        for request in requests:

            if request.catalog_item.catalog.id == "/A/B/C":
                await self._read_csv_files(begin, end, request, report_progress)
                
            else:
                continue

    async def _read_csv_files(
        self, 
        begin: datetime, 
        end: datetime,
        request: ReadRequest, 
        report_progress: Callable[[float], None]
    ):
        sample_period = request.catalog_item.representation.sample_period

        # Cast destination buffer to double elements
        data_view = request.data.cast('d')
        total_elements = len(data_view)
        status_view = request.status

        # Collect all csv file paths under root
        if self.Context.resource_locator is None:
            raise Exception(f"No resource locator provided.")
    
        root_path = self._root = url2pathname(self.Context.resource_locator.path)
        search_pattern = os.path.join(root_path, "*.csv")
        file_paths = glob.glob(search_pattern, recursive=True)

        # Find column in csv file
        properties = request.catalog_item.resource.properties

        if properties is None:
            return
        
        column = cast(int, properties.get("column"))

        # Loop over all files
        for file_path in sorted(file_paths):

            self.Logger.log(LogLevel.Information, f"Processing file {file_path}")

            file_name = os.path.basename(file_path)
            file_date = datetime.strptime(file_name, "%Y-%m-%d.csv").date()

            with open(file_path, newline="") as file:

                reader = csv.reader(file)

                # skip header
                _ = next(reader, None)

                for row in reader:

                    ts_text = row[0] # HH:MM

                    row_dt = datetime.strptime(
                        f"{file_date.isoformat()} {ts_text}",
                        "%Y-%m-%d %H:%M"
                    ).replace(tzinfo=timezone.utc)

                    if row_dt < begin or row_dt >= end:
                        continue

                    # Compute sample index
                    sample_index = int((row_dt - begin) / sample_period)

                    if sample_index < 0 or sample_index >= total_elements:
                        continue

                    # Parse value
                    try:
                        value = float(row[column])
                    except ValueError:
                        continue

                    data_view[sample_index] = value
                    status_view[sample_index] = 1