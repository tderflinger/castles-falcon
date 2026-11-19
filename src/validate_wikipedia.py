"""Validate Wikipedia links in the castles GeoPackage with Great Expectations."""

from pathlib import Path

import great_expectations as gx


def main() -> int:
    """Run the Wikipedia URL validation and return a process exit code."""
    database = Path(__file__).resolve().parent.parent / "castles-falcon.gpkg"
    context = gx.get_context(mode="ephemeral", cloud_mode=False)
    datasource = context.data_sources.add_or_update_sqlite(
        name="castles_falcon",
        connection_string=f"sqlite:///file:{database}?mode=ro&uri=true",
    )
    asset = datasource.add_query_asset(
        name="castlemap_castles",
        query='SELECT wikipedia FROM "castlemap-castles"',
    )
    batch = asset.add_batch_definition_whole_table("whole_table").get_batch()
    suite = context.suites.add(gx.ExpectationSuite(name="castlemap_wikipedia"))
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToMatchRegex(
            column="wikipedia",
            regex=r"^https://.*wikipedia\.org",
            result_format="SUMMARY",
        )
    )
    result = batch.validate(suite)
    print(result.describe())
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
