from .metrics_util import gatk_select_tsv_to_df



def gatk_CalculateContamination_to_df(metric_path, logger):
    select = ["level", "sample"]
    df = gatk_select_tsv_to_df(metric_path, select, logger)
    if df is not None and not df.empty:
        return df
    else:
        return


def run(job_uuid, metric_path, bam, input_state, engine, logger, metric_name) -> None:
    table_name = metric_name
    df = gatk_CalculateContamination_to_df(metric_path, logger)
    if df is not None and not df.empty:
        df["bam"] = bam
        df["input_state"] = input_state
        df["job_uuid"] = job_uuid
        df.to_sql(table_name, engine, if_exists="append")
    return








#def gatk_CalculateContamination_to_df(metric_path, logger):
#    select = ["level", "sample"]
#    df = gatk_select_tsv_to_df(metric_path, select, logger)
#    if df:
#        return df
#    else:
#        return


#def run(job_uuid, metric_path, bam, input_state, engine, logger, metric_name) -> None:
#    table_name = metric_name
#    df = gatk_CalculateContamination_to_df(metric_path, logger)
#    if df:
#        df["bam"] = bam
#        df["input_state"] = input_state
#        df["job_uuid"] = job_uuid
#        df.to_sql(table_name, engine, if_exists="append")
#    return
