# Thesis Results Data

## Overall Architecture Comparison
| architecture   |   total_runs |   repair_rate_percent |   avg_llm_calls |   avg_tokens |
|:---------------|-------------:|----------------------:|----------------:|-------------:|
| multi_agent    |           15 |                 60    |             4.4 |     11371.1  |
| single_agent   |           15 |                 86.67 |             1.8 |      5138.87 |

## Breakdown by Test Complexity
| change_category   | change_name             | architecture   |   total_runs |   repair_rate_percent |   avg_llm_calls |   avg_tokens |
|:------------------|:------------------------|:---------------|-------------:|----------------------:|----------------:|-------------:|
| hard              | error_paradigm_shift    | multi_agent    |            5 |                     0 |             6   |      14865.2 |
| hard              | error_paradigm_shift    | single_agent   |            5 |                    60 |             2.4 |       7050.8 |
| hard              | semantic_split_and_enum | multi_agent    |            5 |                   100 |             2   |       4724.4 |
| hard              | semantic_split_and_enum | single_agent   |            5 |                   100 |             1   |       2617.2 |
| medium            | pagination_and_envelope | multi_agent    |            5 |                    80 |             5.2 |      14523.6 |
| medium            | pagination_and_envelope | single_agent   |            5 |                   100 |             2   |       5748.6 |