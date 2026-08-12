# Research Output Issues

## Issues

| # | item | type | severity | description |
|---|---|---|---|---|
| 1 | figure_existing_shelter_capacity_and_earthquake_related_demand.py | script | minor | A superseded Kumamoto-City-only figure script remains in `src/analyses/` although its output is absent from the current prefecture-wide plan and results inventory. Running all analysis scripts could recreate an unplanned figure based on the former study area and capacity framework. |
| 2 | docs/AnaSOP.md Section 1 | documentation | minor | The final sentence of the central question's required feasibility check still says to proceed to planned output generation, although all nine planned outputs are complete and marked done. This is stale workflow wording and does not affect the analytical results. |

## Severity Summary

| severity | count |
|---|---:|
| critical | 0 |
| major | 0 |
| minor | 2 |

## Recommended Next Steps

- 在后续批量运行分析脚本前，归档或删除已被取代的熊本市旧图脚本，避免重新生成计划外结果；该问题不影响当前正式输出。
- 将AnaSOP中央问题中的流程表述从“继续生成计划输出”改为“计划输出已完成并通过审查”；该问题仅属文档同步。
- 当前没有critical或major问题，可以继续进行 `build-content-dictionary`。
