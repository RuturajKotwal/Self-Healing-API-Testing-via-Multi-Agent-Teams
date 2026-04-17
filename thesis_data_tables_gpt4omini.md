# Thesis Results Data

## Overall Architecture Comparison
| architecture   |   total_runs |   repair_rate_percent |   avg_llm_calls |   avg_tokens |
|:---------------|-------------:|----------------------:|----------------:|-------------:|
| multi_agent    |           15 |                 73.33 |            4.4  |      11547.4 |
| single_agent   |           15 |                100    |            1.67 |       5952.4 |

## Breakdown by Test Complexity
| change_category   | change_name             | architecture   |   total_runs |   repair_rate_percent |   avg_llm_calls |   avg_tokens |
|:------------------|:------------------------|:---------------|-------------:|----------------------:|----------------:|-------------:|
| hard              | error_paradigm_shift    | multi_agent    |            5 |                    20 |             6   |      15134   |
| hard              | error_paradigm_shift    | single_agent   |            5 |                   100 |             2   |       7265   |
| hard              | semantic_split_and_enum | multi_agent    |            5 |                   100 |             2   |       4837   |
| hard              | semantic_split_and_enum | single_agent   |            5 |                   100 |             1   |       3296.8 |
| medium            | pagination_and_envelope | multi_agent    |            5 |                   100 |             5.2 |      14671.2 |
| medium            | pagination_and_envelope | single_agent   |            5 |                   100 |             2   |       7295.4 |