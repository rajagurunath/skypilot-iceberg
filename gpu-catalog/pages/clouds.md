
## Explore Cloud Providers

```sql clouds
 SELECT DISTINCT cloud FROM vms ORDER BY 1
```
<Dropdown
    name=selected_cloud
    data={clouds}
    value=cloud
/>


# 🔎 {inputs.selected_cloud.value} Analytics
```sql cloud_kpis
 SELECT
    COUNT(DISTINCT InstanceType) as total_instance_types,
    COUNT(DISTINCT AcceleratorName) as gpu_types,
    COUNT(DISTINCT Region) as regions,
    AVG(Price) as avg_price,
    AVG(SpotPrice) as avg_spot_price
  FROM vms
  WHERE cloud = '${inputs.selected_cloud.value}'
```

<Value data={cloud_kpis} column=total_instance_types/> Instance Types  
<Value data={cloud_kpis} column=gpu_types/> GPU Types  
<Value data={cloud_kpis} column=regions/> Regions

## GPU Type Pricing

```sql gpu_types
SELECT
    AcceleratorName,
    COUNT(*) as device_count,
    AVG(Price) as avg_price
  FROM vms
  WHERE cloud = '${inputs.selected_cloud.value}' 
--   AND AcceleratorName IS NOT NULL
  GROUP BY AcceleratorName
```

<BarChart 
    data={gpu_types}
    x=AcceleratorName
    y=avg_price
    series=device_count
    title="Average Price per GPU Type"
/>


<!--   
## Price Trends
<Data name="gpu_list" sql="SELECT DISTINCT AcceleratorName FROM vms WHERE cloud = '${cloud}'">
  <select name="selected_gpu" bind:value={selected_gpu}>
    {#each gpu_list as gpu}
    <option value={gpu.AcceleratorName}>{gpu.AcceleratorName}</option>
    {/each}
  </select>
</Data>

{#if selected_gpu}
<Data name="price_trend" sql="
  SELECT
    date,
    Price,
    SpotPrice
  FROM vms
  WHERE cloud = '${cloud}' AND AcceleratorName = '${selected_gpu}'
  ORDER BY date ASC
">
  <Plotly
    data={price_trend}
    type=line
    x=date
    y=Price
    secondaryY=SpotPrice
    title="Price vs Spot Price Trend"
  />
</Data>
{/if} --> -->

<!-- ## Weekend vs Weekday Pricing
<Data name="weekday_analysis" sql="
  SELECT
    CASE WHEN weekday(date) IN (0,6) THEN 'Weekend' ELSE 'Weekday' END as day_type,
    AVG(Price) as avg_price,
    AVG(SpotPrice) as avg_spot_price
  FROM vms
  WHERE cloud = '${cloud}'
  GROUP BY day_type
">
  <Plotly
    data={weekday_analysis}
    type=bar
    x=day_type
    y=['avg_price', 'avg_spot_price']
    title="Weekday vs Weekend Prices"
  />
</Data> -->