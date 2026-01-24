import sys
from collections import defaultdict

import pandas as pd


def run(job_uuid, stats_path, bam, input_state, engine, logger):
    val_error_dict = defaultdict(dict)

    with open(stats_path, "r") as f_open:
        for line in f_open:
            line = line.strip()
            if not line:
                continue
            if line.startswith("ERROR:") or line.startswith("WARNING:"):
                validation_type = line.split(":")[0]
                line_split = [x.strip() for x in line.split(",")]
                # Join all fields after the first one or two columns
                line_error = (
                    ", ".join(line_split[1:]) if len(line_split) > 1 else line_split[0]
                )
                val_error_dict[validation_type][line_error] = (
                    val_error_dict[validation_type].get(line_error, 0) + 1
                )
            elif line.startswith("No errors found"):
                validation_type = "PASS"
                line_error = line
                val_error_dict[validation_type][line_error] = 1
            else:
                logger.warning("Unknown Picard validation line, skipping: %s", line)
                continue

    # Write to SQLite
    for validation_type in ["ERROR", "WARNING", "PASS"]:
        for akey in sorted(val_error_dict[validation_type].keys()):
            store_dict = {
                "value": akey,
                "count": val_error_dict[validation_type][akey],
                "job_uuid": job_uuid,
                "bam": bam,
                "severity": validation_type,
                "input_state": input_state,
            }
            df = pd.DataFrame([store_dict])
            table_name = "picard_ValidateSamFile"
            df.to_sql(table_name, engine, if_exists="append", index=False)

    return
