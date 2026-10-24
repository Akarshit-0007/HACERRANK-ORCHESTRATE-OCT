import os

def generate_usage_report(output_dir: str, total_rows: int , total_input_tokens: int, total_output_tokens: int):
    """
    Calculate statistics and writes the required usage_report.md file.
    :param output_dir:
    :param total_rows:
    :param total_input_tokens:
    :param total_output_tokens:
    :return:
    """

    avg_input = total_input_tokens / total_rows if total_rows > 0 else 0
    avg_output = total_output_tokens / total_rows if total_rows > 0 else 0
    combined_tokens = (total_input_tokens / 1_000_000 * 0.30) + (total_output_tokens / 1_000_000 * 2.50)

    report_content = f"""# Pipeline Usage and Token Cost Report

    ## 1. Execution Overview
    - **Dataset Evaluated:** `deletion_requests.csv`
    - **Total Rows Processed:** {total_rows}
    - **Primary Model Provider:** Google AI Studio
    - **Primary Model Used:** `gemini-2.5-flash`

    ## 2. Per-Model Statistics (`gemini-2.5-flash`)
    - **Total Model Calls:** {total_rows}
    - **Total Input Tokens:** {total_input_tokens}
    - **Average Input Tokens / Request:** {avg_input:.2f}
    - **Total Output Tokens:** {total_output_tokens}
    - **Average Output Tokens / Request:** {avg_output:.2f}
    - **Combined Total Tokens:** {combined_tokens}

    ## 3. Cost Estimation Breakdown
    - **Estimated Total Project Cost (Paid Tier Equivalent):** ${est_cost:.5f}
    - **Actual Invoiced Cost (Free Tier):** $0.00
    """

    report_path = os.path.join(output_dir, "usage_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"[INFO] usage_report.md generated successfully at: {report_path}")