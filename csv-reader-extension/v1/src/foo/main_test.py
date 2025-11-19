from urllib.parse import urlparse

import pytest
from nexus_extensibility import (DataSourceContext, ILogger,  # type: ignore
                                 LogLevel, ResourceCatalog)

from .main import CsvReader, CsvReaderSettings


class TestLogger(ILogger):
    def log(self, log_level: LogLevel, message: str):
        pass

@pytest.mark.asyncio
async def test_enrich_catalog():

    # Arrange
    reader = CsvReader()
    settings = CsvReaderSettings(dummy="dummy")

    context = DataSourceContext[CsvReaderSettings](
        resource_locator=urlparse("file:///data"),
        source_configuration=settings,
        request_configuration=None
    )

    logger = TestLogger()

    await reader.set_context(context, logger)

    # Act
    catalog = await reader.enrich_catalog(ResourceCatalog("/A/B/C"))

    # Assert
    assert catalog.resources
    resource_ids = [resource.id for resource in catalog.resources]
    assert "wind_speed" in resource_ids
    assert "wind_direction" in resource_ids

# @pytest.mark.asyncio
# async def test_read_csv_range(tmp_path):
#     # Arrange
#     reader = main.CsvReader()

#     # Fake context with resource locator path pointing to existing data folder
#     data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data"))

#     class ResourceLocator:
#         def __init__(self, path: str):
#             self.path = path

#     class Context:
#         def __init__(self, rl):
#             self.resource_locator = rl

#     reader.Context = Context(ResourceLocator(data_dir))

#     # Build catalog (reuse production method)
#     class DummyCatalog:
#         def __init__(self, id: str):
#             self.id = id

#     catalog = await reader.enrich_catalog(DummyCatalog("/A/B/C"))

#     # Helper: create minimal catalog_item objects
#     class CatalogItem:
#         def __init__(self, catalog, resource, representation):
#             self.catalog = catalog
#             self.resource = resource
#             self.representation = representation

#     wind_speed_res = next(r for r in catalog.resources if r.id == "wind_speed")
#     wind_dir_res = next(r for r in catalog.resources if r.id == "wind_direction")

#     rep_speed = wind_speed_res.representations[0]
#     rep_dir = wind_dir_res.representations[0]

#     # Time range (first 2 hours of 2020-01-01)
#     begin = datetime(2020, 1, 1, 0, 10, tzinfo=timezone.utc)
#     end = datetime(2020, 1, 1, 2, 0, tzinfo=timezone.utc)  # exclusive
#     sample_period: timedelta = rep_speed.sample_period
#     samples = int((end - begin) / sample_period)

#     # Allocate buffers
#     data_speed = bytearray(samples * 8)
#     data_dir = bytearray(samples * 8)
#     status_speed = bytearray(samples)
#     status_dir = bytearray(samples)

#     # Dummy ReadRequest objects matching interface used in main.py
#     class ReadRequest:
#         def __init__(self, resource_id, catalog_item, data, status):
#             self.resource_id = resource_id
#             self.catalog_item = catalog_item
#             self.data = memoryview(data)
#             self.status = memoryview(status)

#     req_speed = ReadRequest("wind_speed", CatalogItem(catalog, wind_speed_res, rep_speed), data_speed, status_speed)
#     req_dir = ReadRequest("wind_direction", CatalogItem(catalog, wind_dir_res, rep_dir), data_dir, status_dir)

#     progress_events = []

#     def report_progress(p: float):
#         progress_events.append(p)

#     # Act
#     await reader.read(begin, end, [req_speed, req_dir], lambda *args, **kwargs: None, report_progress)

#     # Assert: derive expected values from CSV file (column indices 1 and 2)
#     expected_speed = []
#     expected_dir = []

#     file_path = os.path.join(data_dir, "2020-01-01.csv")
#     with open(file_path, newline="") as f:
#         r = csv.reader(f)
#         _ = next(r, None)
#         for row in r:
#             row_time = datetime.strptime(f"2020-01-01 {row[0]}", "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
#             if row_time < begin or row_time >= end:
#                 continue
#             expected_speed.append(float(row[1]))
#             expected_dir.append(float(row[2]))

#     assert len(expected_speed) == samples
#     assert len(expected_dir) == samples

#     import array, struct

#     speed_values = array.array('d')
#     dir_values = array.array('d')
#     speed_values.frombytes(req_speed.data.tobytes())
#     dir_values.frombytes(req_dir.data.tobytes())

#     # Compare populated entries only (status == 1)
#     for i in range(samples):
#         if req_speed.status[i] == 1:
#             assert speed_values[i] == expected_speed[i]
#         if req_dir.status[i] == 1:
#             assert dir_values[i] == expected_dir[i]

#     # Ensure all samples in range got filled
#     assert all(s == 1 for s in req_speed.status)
#     assert all(s == 1 for s in req_dir.status)