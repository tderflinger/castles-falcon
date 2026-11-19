"""Validate castle QIDs and Wikipedia links with Great Expectations."""

from pathlib import Path

import great_expectations as gx
from great_expectations.checkpoint import Checkpoint
from great_expectations.checkpoint.actions import UpdateDataDocsAction
from great_expectations.core import ValidationDefinition


def main() -> int:
    """Run the Wikipedia URL validation and return a process exit code."""
    project_root = Path(__file__).resolve().parent.parent / "reports"
    database = Path(__file__).resolve().parent.parent / "castles-falcon.gpkg"
    context = gx.get_context(mode="file", project_root_dir=str(project_root))

    try:
        datasource = context.data_sources.get("castles_falcon")
    except LookupError:
        datasource = context.data_sources.add_or_update_sqlite(
            name="castles_falcon",
            connection_string=f"sqlite:///file:{database}?mode=ro&uri=true",
        )

    try:
        asset = datasource.get_asset("castlemap_castles")
    except LookupError:
        asset = datasource.add_query_asset(
            name="castlemap_castles",
            query='SELECT wikipedia FROM "castlemap-castles"',
        )

    try:
        batch_definition = asset.get_batch_definition("whole_table")
    except LookupError:
        batch_definition = asset.add_batch_definition_whole_table("whole_table")

    try:
        qid_asset = datasource.get_asset("castlemap_qid")
    except LookupError:
        qid_asset = datasource.add_query_asset(
            name="castlemap_qid",
            query='SELECT qid FROM "castlemap-castles"',
        )

    try:
        qid_batch_definition = qid_asset.get_batch_definition("whole_table")
    except LookupError:
        qid_batch_definition = qid_asset.add_batch_definition_whole_table(
            "whole_table"
        )

    suite_names = {existing_suite.name for existing_suite in context.suites.all()}
    if "castlemap_wikipedia" in suite_names:
        suite = context.suites.get("castlemap_wikipedia")
    else:
        suite = context.suites.add(gx.ExpectationSuite(name="castlemap_wikipedia"))
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToMatchRegex(
            column="wikipedia",
            regex=r"^https://.*wikipedia\.org",
            result_format="SUMMARY",
        )
    )
    if "castlemap_qid" in suite_names:
        qid_suite = context.suites.get("castlemap_qid")
    else:
        qid_suite = context.suites.add(gx.ExpectationSuite(name="castlemap_qid"))
    qid_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToMatchRegex(
            column="qid",
            regex=r"^Q[0-9]+$",
            result_format="SUMMARY",
        )
    )

    validation_definition_names = {
        definition.name for definition in context.validation_definitions.all()
    }
    if "castlemap_wikipedia_validation" in validation_definition_names:
        validation_definition = context.validation_definitions.get(
            "castlemap_wikipedia_validation"
        )
    else:
        validation_definition = context.validation_definitions.add(
            ValidationDefinition(
                name="castlemap_wikipedia_validation",
                data=batch_definition,
                suite=suite,
            )
        )
    if "castlemap_qid_validation" in validation_definition_names:
        qid_validation_definition = context.validation_definitions.get(
            "castlemap_qid_validation"
        )
    else:
        qid_validation_definition = context.validation_definitions.add(
            ValidationDefinition(
                name="castlemap_qid_validation",
                data=qid_batch_definition,
                suite=qid_suite,
            )
        )
    validation_definitions = [validation_definition, qid_validation_definition]

    checkpoint_names = {
        checkpoint.name for checkpoint in context.checkpoints.all()
    }
    if "castlemap_wikipedia_checkpoint" in checkpoint_names:
        checkpoint = context.checkpoints.get("castlemap_wikipedia_checkpoint")
        changed = False
        existing_validation_names = {
            definition.name for definition in checkpoint.validation_definitions
        }
        missing_validation_definitions = [
            definition
            for definition in validation_definitions
            if definition.name not in existing_validation_names
        ]
        if missing_validation_definitions:
            checkpoint.validation_definitions = [
                *checkpoint.validation_definitions,
                *missing_validation_definitions,
            ]
            changed = True
        if not any(
            isinstance(action, UpdateDataDocsAction) for action in checkpoint.actions
        ):
            checkpoint.actions = [
                *checkpoint.actions,
                UpdateDataDocsAction(name="update_data_docs"),
            ]
            changed = True
        if changed:
            checkpoint.save()
    else:
        checkpoint = context.checkpoints.add(
            Checkpoint(
                name="castlemap_wikipedia_checkpoint",
                validation_definitions=validation_definitions,
                actions=[UpdateDataDocsAction(name="update_data_docs")],
            )
        )

    result = checkpoint.run()
    print(result.describe())
    for validation_result_id, validation_result in result.run_results.items():
        print(
            f"validation: batch={validation_result_id.batch_identifier} "
            f"suite={validation_result.suite_name} "
            f"success={validation_result.success}"
        )
        for expectation_result in validation_result.results:
            expectation = expectation_result.expectation_config
            if expectation_result.success:
                status = "PASS"
            elif not expectation_result.result:
                status = "ERROR"
            else:
                status = "FAIL"
            print(f"  {status} {expectation.type} {expectation.kwargs}")
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
