# Thesis Results Data

## Overall Architecture Comparison
| architecture   |   total_runs |   repair_rate_percent |   avg_llm_calls |   avg_tokens |
|:---------------|-------------:|----------------------:|----------------:|-------------:|
| multi_agent    |           15 |                 73.33 |            4.53 |     12026.9  |
| single_agent   |           15 |                 80    |            2.07 |      6294.87 |

## Breakdown by Test Complexity
| change_category   | change_name             | architecture   |   total_runs |   repair_rate_percent |   avg_llm_calls |   avg_tokens |
|:------------------|:------------------------|:---------------|-------------:|----------------------:|----------------:|-------------:|
| hard              | error_paradigm_shift    | multi_agent    |            5 |                    40 |             6   |      15339.6 |
| hard              | error_paradigm_shift    | single_agent   |            5 |                    40 |             3.2 |      10034.4 |
| hard              | semantic_split_and_enum | multi_agent    |            5 |                   100 |             2   |       4575.4 |
| hard              | semantic_split_and_enum | single_agent   |            5 |                   100 |             1   |       2869.2 |
| medium            | pagination_and_envelope | multi_agent    |            5 |                    80 |             5.6 |      16165.8 |
| medium            | pagination_and_envelope | single_agent   |            5 |                   100 |             2   |       5981   |