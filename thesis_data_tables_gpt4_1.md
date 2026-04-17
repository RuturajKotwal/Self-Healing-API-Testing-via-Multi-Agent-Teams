# Thesis Results Data

## Overall Architecture Comparison
| architecture   |   total_runs |   repair_rate_percent |   avg_llm_calls |   avg_tokens |
|:---------------|-------------:|----------------------:|----------------:|-------------:|
| multi_agent    |           15 |                100    |            3.33 |      9851.27 |
| single_agent   |           15 |                 93.33 |            1.73 |      7150.93 |

## Breakdown by Test Complexity
| change_category   | change_name             | architecture   |   total_runs |   repair_rate_percent |   avg_llm_calls |   avg_tokens |
|:------------------|:------------------------|:---------------|-------------:|----------------------:|----------------:|-------------:|
| hard              | error_paradigm_shift    | multi_agent    |            5 |                   100 |             4   |      11450   |
| hard              | error_paradigm_shift    | single_agent   |            5 |                   100 |             1.8 |       7441.6 |
| hard              | semantic_split_and_enum | multi_agent    |            5 |                   100 |             2   |       5465.2 |
| hard              | semantic_split_and_enum | single_agent   |            5 |                   100 |             1   |       3700.8 |
| medium            | pagination_and_envelope | multi_agent    |            5 |                   100 |             4   |      12638.6 |
| medium            | pagination_and_envelope | single_agent   |            5 |                    80 |             2.4 |      10310.4 |