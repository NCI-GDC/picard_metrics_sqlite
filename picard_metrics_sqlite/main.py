#!/usr/bin/env python

import argparse
import logging
import os
import sys
from typing import Any

import sqlalchemy

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
    logger = logging.getLogger(__name__)
    return logger


def main() -> int:
    parser = argparse.ArgumentParser("picard/gatk metrics to sqlite tool")

    # Logging flags.
    parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        const=logging.DEBUG,
        dest="level",
        help="Enable debug logging.",
    )
    parser.set_defaults(level=logging.INFO)

    # Required flags.
    parser.add_argument("--input_state", required=True)
    parser.add_argument("--metric_name", required=True, help="picard tool")
    parser.add_argument("--metric_path", required=False)
    parser.add_argument(
        "--job_uuid",
        required=True,
        help="uuid string",
    )

    # Tool flags
    parser.add_argument("--bam", required=False)
    parser.add_argument("--fasta", required=False)
    parser.add_argument("--ref_flat", required=False)
    parser.add_argument("--ribosomal_intervals", required=False)
    parser.add_argument("--vcf", required=False)

    # cmm
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

    # setup required parameters
    args = parser.parse_args()
    input_state = args.input_state
    metric_name = args.metric_name
    metric_path = args.metric_path
    job_uuid = args.job_uuid

    logger = setup_logging("picard_" + metric_name, args, job_uuid)

    sqlite_name = job_uuid + ".db"
    engine_path = "sqlite:///" + sqlite_name
    engine = sqlalchemy.create_engine(engine_path, isolation_level="SERIALIZABLE")

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
        input_state = get_param(args, "input_state")
        picard_collecthsmetrics.run(
            job_uuid, metric_path, bam, input_state, engine, logger, metric_name
        )
    elif metric_name == "CollectMultipleMetrics":
        bam = get_param(args, "bam")
        input_state = get_param(args, "input_state")
        alignment_summary_metrics = get_param(args, "alignment_summary_metrics")
        bait_bias_detail_metrics = get_param(args, "bait_bias_detail_metrics")
        bait_bias_summary_metrics = get_param(args, "bait_bias_summary_metrics")
        base_distribution_by_cycle_metrics = get_param(
            args, "base_distribution_by_cycle_metrics"
        )
        gc_bias_detail_metrics = get_param(args, "gc_bias_detail_metrics")
        gc_bias_summary_metrics = get_param(args, "gc_bias_summary_metrics")
        insert_size_metrics = get_param(args, "insert_size_metrics")
        pre_adapter_detail_metrics = get_param(args, "pre_adapter_detail_metrics")
        pre_adapter_summary_metrics = get_param(args, "pre_adapter_summary_metrics")
        quality_by_cycle_metrics = get_param(args, "quality_by_cycle_metrics")
        quality_distribution_metrics = get_param(args, "quality_distribution_metrics")
        quality_yield_metrics = get_param(args, "quality_yield_metrics")
        picard_collectmultiplemetrics.run(
            bam,
            engine,
            input_state,
            logger,
            job_uuid,
            alignment_summary_metrics,
            bait_bias_detail_metrics,
            bait_bias_summary_metrics,
            base_distribution_by_cycle_metrics,
            gc_bias_detail_metrics,
            gc_bias_summary_metrics,
            insert_size_metrics,
            pre_adapter_detail_metrics,
            pre_adapter_summary_metrics,
            quality_by_cycle_metrics,
            quality_distribution_metrics,
            quality_yield_metrics,
        )
    elif metric_name == "CollectOxoGMetrics":
        bam = get_param(args, "bam")
        input_state = get_param(args, "input_state")
        picard_collectoxogmetrics.run(
            job_uuid, metric_path, bam, input_state, engine, logger, metric_name
        )
    elif metric_name == "CollectRnaSeqMetrics":
        bam = get_param(args, "bam")
        input_state = get_param(args, "input_state")
        picard_collectrnaseqmetrics.run(
            job_uuid, metric_path, bam, input_state, engine, logger, metric_name
        )
    elif metric_name == "CollectTargetedPcrMetrics":
        bam = get_param(args, "bam")
        input_state = get_param(args, "input_state")
        picard_collecttargetedpcrmetrics.run(
            job_uuid, metric_path, bam, input_state, engine, logger, metric_name
        )
    elif metric_name == "CollectWgsMetrics":
        bam = get_param(args, "bam")
        input_state = get_param(args, "input_state")
        picard_collectwgsmetrics.run(
            job_uuid, metric_path, bam, input_state, engine, logger, metric_name
        )
    elif metric_name == "MarkDuplicates":
        bam = get_param(args, "bam")
        input_state = get_param(args, "input_state")
        picard_markduplicates.run(
            job_uuid, metric_path, bam, input_state, engine, logger, metric_name
        )
    # elif metric_name == 'MarkDuplicatesWithMateCigar':
    #     bam = get_param(args, 'bam')
    #     input_state = get_param(args, 'input_state')
    #     picard_markduplicateswithmatecigar.run(job_uuid, bam, input_state, engine, logger)
    # elif metric_name == 'FixMateInformation':
    #     bam = get_param(args, 'bam')
    #     input_state = get_param(args, 'input_state')
    #     picard_fixmateinformation.run(job_uuid, bam, input_state, engine, logger)
    elif metric_name == "ValidateSamFile":
        bam = get_param(args, "bam")
        input_state = get_param(args, "input_state")
        picard_validatesamfile.run(
            job_uuid, metric_path, bam, input_state, engine, logger
        )
    else:
        sys.exit("No recognized tool was selected")

    return 0


if __name__ == "__main__":
    main()
