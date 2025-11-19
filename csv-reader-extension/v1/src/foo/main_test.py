from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import pytest
from nexus_extensibility import (CatalogItem,  # type: ignore
                                 DataSourceContext, ILogger, LogLevel,
                                 ReadRequest, ResourceCatalog)

from .main import CsvReader, CsvReaderSettings


class TestLogger(ILogger):
    def log(self, log_level: LogLevel, message: str):
        pass

@pytest.mark.asyncio
async def test_enrich_catalog():

    # Arrange
    csv_reader = CsvReader()
    settings = CsvReaderSettings(dummy="dummy")

    context = DataSourceContext[CsvReaderSettings](
        resource_locator=urlparse((Path(__file__).parent / "../../../../data").resolve().as_uri()),
        source_configuration=settings,
        request_configuration=None
    )

    logger = TestLogger()

    await csv_reader.set_context(context, logger)

    # Act
    catalog = await csv_reader.enrich_catalog(ResourceCatalog("/A/B/C"))

    # Assert
    assert catalog.resources
    resource_ids = [resource.id for resource in catalog.resources]
    assert "wind_speed" in resource_ids
    assert "wind_direction" in resource_ids

@pytest.mark.asyncio
async def test_read():

    # Arrange
    csv_reader = CsvReader()
    settings = CsvReaderSettings(dummy="dummy")

    context = DataSourceContext[CsvReaderSettings](
        resource_locator=urlparse((Path(__file__).parent / "../../../../data").resolve().as_uri()),
        source_configuration=settings,
        request_configuration=None
    )

    logger = TestLogger()

    await csv_reader.set_context(context, logger)
    catalog = await csv_reader.enrich_catalog(ResourceCatalog("/A/B/C"))
    assert catalog.resources

    begin = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    end = datetime(2020, 1, 2, 0, 0, tzinfo=timezone.utc)

    # -> read_request 1 (wind_speed)
    resource = catalog.resources[0]

    assert resource.representations
    representation = resource.representations[0]

    catalog_item = CatalogItem(
        catalog,
        resource,
        representation,
        parameters=None
    )

    samples = int((end - begin) / representation.sample_period)
    data_wind_speed = memoryview(bytearray(samples * representation.element_size))
    status_wind_speed = memoryview(bytearray(samples))

    read_request_1 = ReadRequest(
        resource.id,
        catalog_item,
        data_wind_speed,
        status_wind_speed
    )

    # -> read_request 2 (wind_direction)
    resource = catalog.resources[1]

    assert resource.representations
    representation = resource.representations[0]

    catalog_item = CatalogItem(
        catalog,
        resource,
        representation,
        parameters=None
    )

    samples = int((end - begin) / representation.sample_period)
    data_wind_dir = memoryview(bytearray(samples * representation.element_size))
    status_wind_dir = memoryview(bytearray(samples))

    read_request_2 = ReadRequest(
        resource.id,
        catalog_item,
        data_wind_dir,
        status_wind_dir
    )

    read_requests = [read_request_1, read_request_2]

    # Act
    await csv_reader.read(
        begin=begin,
        end=end,
        requests=read_requests,
        read_data=None, # type: ignore
        report_progress=lambda x: None
    )

    # Assert
    expected_wind_speed = [4.7, 5.2]
    actual_wind_speed = data_wind_speed.cast('d')

    assert expected_wind_speed[0] == actual_wind_speed[0]
    assert expected_wind_speed[1] == actual_wind_speed[1]

    assert status_wind_speed[0] == 1
    assert status_wind_speed[1] == 1
    
    expected_wind_dir = [306, 310]
    actual_wind_dir = data_wind_dir.cast('d')

    assert expected_wind_dir[0] == actual_wind_dir[0]
    assert expected_wind_dir[1] == actual_wind_dir[1]

    assert status_wind_dir[0] == 1
    assert status_wind_dir[1] == 1