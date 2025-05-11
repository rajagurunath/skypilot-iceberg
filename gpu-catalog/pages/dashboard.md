# 💸 GPU & CPU Price Analytics Dashboard

## 🌎 Global Cloud KPIs
```sql global_kpis
   SELECT
    COUNT(DISTINCT cloud) as clouds,
    COUNT(DISTINCT InstanceType) as instance_types,
    COUNT(DISTINCT Region) as regions,
    COUNT(DISTINCT AcceleratorName) as gpu_types
  FROM vms;
```


<Value data={global_kpis} column=clouds/> Cloud Providers  
<Value data={global_kpis} column=instance_types/> Instance Types  
<Value data={global_kpis} column=regions/> Regions  
<Value data={global_kpis} column=gpu_types/> GPU Types


## Average GPU Prices by Cloud
```sql gpu_pricing
   SELECT
    cloud,
    AcceleratorName,
    AVG(Price) as avg_price,
    COUNT(DISTINCT InstanceType) as instance_types,
    COUNT(*) as total_devices
  FROM vms
--   WHERE AcceleratorName IS NOT NULL
  GROUP BY cloud, AcceleratorName
```

<!-- <Plotly
    data={gpu_pricing}
    type=scatter
    x=AcceleratorName
    y=avg_price
    color=cloud
    size=total_devices
    title="Average GPU Prices by Cloud"
/> -->
<ScatterPlot 
    data={gpu_pricing}
    x=AcceleratorName
    y=avg_price
    series=cloud
    title="Average GPU Prices by Cloud"
/>
