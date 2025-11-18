## 性能评估与可扩展性测试计划

1. **测试变量**
   - `batch_size`：每次 `GenerateAirQualityData` 写入的记录条数，建议取值 20、50、100；
   - `station_count`：模拟的监测站点数量，建议 6~20；
   - `schedule`：Timer Trigger 频率，例如 1 分钟/两分钟，模拟不同写入速率；
   - `iterations`：每种配置下执行的批次数（可在 `load_test.py` 指定，便于采集稳定数据）。

2. **数据采集**
   - 在 Azure Portal 查看每个 Function 的监控面板，记录 `Duration`（平均执行时间）、`Memory Working Set`（范围/平均）、`CPU Time`；
   - 使用 Log Analytics 执行如下查询，提取多个负载下的关键指标（替换 `FunctionName`）：

     ```kusto
     requests
     | where name == "GenerateAirQualityData"
     | summarize avgDuration=avg(duration), maxMemory=max(customDimensions["MemoryWorkingSet"]), count() by bin(timestamp, 5m), tostring(customDimensions["InvocationId"])
     ```

   - 也可在 `ProcessAirQualitySummary` 中记录 `len(records)`、`window_start`/`window_end`，用日志文件附带 `batch_size` 信息，方便对照。

3. **可扩展性分析**
   - 比较多组负载下的平均 Duration 与资源指标，观察是否成线性增长或出现拐点；
   - 记录在高写入率下是否触发函数 App 的自动扩展（如 Instance Count、Cold Start）；
   - 统计 `air_quality_summary` 表中记录数随时间的增长趋势，验证 Change Tracking 准确处理新增数据。

4. **结果呈现建议**
   - 在报告中以表格列出每组负载的 `batch_size`/`duration`/`record_count`、所需 `CPU`/`Memory`，并附上相关的 Azure Monitor 图表截图；
   - 在演示视频中说明负载测试步骤、实际观察到的性能变化；
   - 可选：把数据导出到 CSV，再用 Excel/Markdown 绘制条形图以展示时间与资源消耗之间的关系。
