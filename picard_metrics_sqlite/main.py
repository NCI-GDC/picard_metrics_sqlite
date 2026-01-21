#!/usr/bin/env python

import argparse
import logging
import os
import sys
from typing import Any

import sqlalchemy
from sqlalchemy import text

from picard_metrics_sqlite.metrics import (
    gatk_calculatecontamination,
    picard_collectalignmentsummarymetrics,
    picard_collecthsmetrics,
    picard_collectmultiplemetrics,
    picard_collectoxogmetrics,
    picard_collectrnaseqmetrics,
    picard_collecttargetedpcrmetrics,
    picard_collectwgsmetrics,
    picard_markduplicates,
    picard_validatesamfile,
)


def get_param(args: argparse.Namespace, param_name: str) -> Any:
    return vars(args)[param_name]


def setup_logging(
    tool_name: str, args: argparse.Namespace, job_uuid: str
) -> logging.Logger:
    logging.basicConfig(
        filename=os.path.join(f"{job_uuid}_{tool_name}.log"),
        level=args.level,
        filemode="w",
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d_%H:%M:%S_%Z",
    )
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    return logging.getLogger(__name__)


def ensure_db_exists(engine: sqlalchemy.Engine) -> None:
    """
    Forces SQLite file creation and a committed transaction.
    Required so downstream tools (merge_sqlite, CWL) see the DB.
    """
    with engine.begin() as conn:
        conn.execute(text("SELECT 1"))


def db_has_data(engine: sqlalchemy.Engine) -> bool:
    """
    Returns True if at least one user table has >=1 row.
    """
    with engine.connect() as conn:
        tables = conn.execute(
            text(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                  AND name NOT LIKE 'sqlite_%'
                """
            )
        ).fetchall()

        for (table,) in tables:
            count = conn.execute(
                text(f'SELECT COUNT(*) FROM "{table}"')
            ).scalar_one()
            if count > 0:
                return True

    return False


def main() -> int:
    parser = argparse.ArgumentParser("picard/gatk metrics to sqlite tool")

    # Logging flags
    parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        const=logging.DEBUG,
        dest="level",
        help="Enable debug logging.",
    )
    parser.set_defaults(level=logging.INFO)

    # Required flags
    parser.add_argument("--input_state", required=True)
    parser.add_argument("--metric_name", required=True, help="picard tool")
    parser.add_argument("--metric_path", required=False)
    parser.add_argument("--job_uuid", required=True, help="uuid string")

    # Tool flags
    parser.add_argument("--bam", required=False)
    parser.add_argument("--fasta", required=False)
    parser.add_argument("--ref_flat", required=False)
    parser.add_argument("--ribosomal_intervals", required=False)
    parser.add_argument("--vcf", required=False)

    # CollectMultipleMetrics flags
    parser.add_argument("--alignment_summary_metrics", required=False)
    parser.add_argument("--bait_bias_detail_metrics", required=False)
    parser.add_argument("--bait_bias_summary_metrics", required=False)
    parser.add_argument("--base_distribution_by_cycle_metrics", required=False)
    parser.add_argument("--gc_bias_detail_metrics", required=False)
    parser.add_argument("--gc_bias_summary_metrics", required=False)
    parser.add_argument("--insert_size_metrics", required=False)
    parser.add_argument("--pre_adapter_detail_metrics", required=False)
    parser.add_argument("--pre_adapter_summary_metrics", required=False)
    parser.add_argument("--quality_by_cycle_metrics", required=False)
    parser.add_argument("--quality_distribution_metrics", required=False)
    parser.add_argument("--quality_yield_metrics", required=False)

    args = parser.parse_args()

    input_state = args.input_state
    metric_name = args.metric_name
    metric_path = args.metric_path
    job_uuid = args.job_uuid

    logger = setup_logging("picard_" + metric_name, args, job_uuid)

    sqlite_name = f"{job_uuid}.db"
    engine_path = f"sqlite:///{sqlite_name}"
    engine = sqlalchemy.create_engine(
        engine_path,
        isolation_level="SERIALIZABLE",
        future=True,
    )

    #  Critical fix: ensure DB file + transaction exist
    ensure_db_exists(engine)

    if metric_name == "gatk_CalculateContamination":
        bam = get_param(args, "bam")
        gatk_calculatecontamination.run(
            job_uuid, metric_path, bam, input_state, engine, logger, metric_name
        )

    elif metric_name == "CollectAlignmentSummaryMetrics":
        bam = get_param(args, "bam")
        picard_collectalignmentsummarymetrics.run(
            job_uuid, metric_path, bam, input_state, engine, logger, metric_name
        )

    elif metric_name == "CollectHsMetrics":
        bam = get_param(args, "bam")
        picard_collecthsmetrics.run(
            job_uuid, metric_path, bam, input_state, engine, logger, metric_name
        )

    elif metric_name == "CollectMultipleMetrics":
        bam = get_param(args, "bam")
        picard_collectmultiplemetrics.run(
            bam,
            engine,
            input_state,
            logger,
            job_uuid,
            get_param(args, "alignment_summary_metrics"),
            get_param(args, "bait_bias_detail_metrics"),
            get_param(args, "bait_bias_summary_metrics"),
            get_param(args, "base_distribution_by_cycle_metrics"),
            get_param(args, "gc_bias_detail_metrics"),
            get_param(args, "gc_bias_summary_metrics"),
            get_param(args, "insert_size_metrics"),
            get_param(args, "pre_adapter_detail_metrics"),
            get_param(args, "pre_adapter_summary_metrics"),
            get_param(args, "quality_by_cycle_metrics"),
            get_param(args, "quality_distribution_metrics"),
            get_param(args, "quality_yield_metrics"),
        )

    elif metric_name == "CollectOxoGMetrics":
        bam = get_param(args, "bam")
        picard_collectoxogmetrics.run(
            job_uuid, metric_path, bam, input_state, engine, logger, metric_name
        )

    elif metric_name == "CollectRnaSeqMetrics":
        bam = get_param(args, "bam")
        picard_collectrnaseqmetrics.run(
            job_uuid, metric_path, bam, input_state, engine, logger, metric_name
        )

    elif metric_name == "CollectTargetedPcrMetrics":
        bam = get_param(args, "bam")
        picard_collecttargetedpcrmetrics.run(
            job_uuid, metric_path, bam, input_state, engine, logger, metric_name
        )

    elif metric_name == "CollectWgsMetrics":
        bam = get_param(args, "bam")
        picard_collectwgsmetrics.run(
            job_uuid, metric_path, bam, input_state, engine, logger, metric_name
        )

    elif metric_name == "MarkDuplicates":
        bam = get_param(args, "bam")
        picard_markduplicates.run(
            job_uuid, metric_path, bam, input_state, engine, logger, metric_name
        )

    elif metric_name == "ValidateSamFile":
        bam = get_param(args, "bam")
        picard_validatesamfile.run(
            job_uuid, metric_path, bam, input_state, engine, logger
        )

    else:
        sys.exit("No recognized tool was selected")

    # Final safety: DB must contain data
    if not db_has_data(engine):
        raise RuntimeError(
            f"SQLite database '{sqlite_name}' was created but contains no data"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())

