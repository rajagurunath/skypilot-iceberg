# 📚 Welcome to GPU & CPU Price Analytics Dashboard!

### What this app offers:
- View real-time **GPU & CPU prices** across **16+ cloud providers**
- Deep dive into specific cloud providers' offerings
- Analyze trends, spot prices, and historical shifts
- Instantly compare **weekday vs weekend** price behaviors

All Thanks to [Skypilot-Catalog](https://github.com/skypilot-org/skypilot-catalog)! 🚀 

**Built using**:
- Skypilot-Catalog
- Evidence
- DuckDB
- Iceberg Table Format
- Cloudflare R2

<Link href="/dashboard">Explore Dashboard →</Link>
<Details title='How to edit this page'>

  This page can be found in your project at `/pages/index.md`. Make a change to the markdown file and save it to see the change take effect in your browser.
</Details>

```sql categories
 show databases ;
```

```sql ttt
 show tables;
```


```sql global_kpis
   SELECT
    COUNT(DISTINCT cloud) as clouds,
    COUNT(DISTINCT InstanceType) as instance_types,
    COUNT(DISTINCT Region) as regions,
    COUNT(DISTINCT AcceleratorName) as gpu_types
  FROM vms;
```
