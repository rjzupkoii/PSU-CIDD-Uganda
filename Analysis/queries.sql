-- Basic monitoring query
select c.id as configurationid, replicateid, filename,
  to_date('2004-01-01', 'YYYY-MM-DD') + max(dayselapsed) as modeldata, max(dayselapsed) as dayselapsed,
  starttime, now() - starttime as runningtime
from sim.replicate r
  inner join sim.configuration c on c.id = r.configurationid
  inner join sim.monthlydata md on md.replicateid = r.id
where r.endtime is null
group by c.id, replicateid, filename, starttime
order by dayselapsed desc

-- Query for the replicate count
select c.filename, count(r.id) as replicates, 
  sum(case when r.endtime is not null then 1 else 0 end) as complete
from sim.configuration c
  inner join sim.replicate r on c.id = r.configurationid
where c.studyid = 5
group by c.filename
order by c.filename

-- Query for IRS data
SELECT a.*, 
	CASE WHEN b.occurrences IS NULL THEN 0 ELSE b.occurrences END as occurances,
	CASE WHEN b.clinicaloccurrences IS NULL THEN 0 ELSE b.clinicaloccurrences END as clinicaloccurrences,
	CASE WHEN b.weightedoccurrences IS NULL THEN 0 ELSE b.weightedoccurrences END as weightedoccurrences
FROM (
  SELECT c.filename, r.id, md.dayselapsed, 
	msd.infectedindividuals, msd.clinicalepisodes, msd.treatments, msd.treatmentfailures  
  FROM sim.configuration c
	INNER JOIN sim.replicate r ON r.configurationid = c.id
	INNER JOIN sim.monthlydata md ON md.replicateid = r.id
	INNER JOIN sim.monthlysitedata msd ON msd.monthlydataid = md.id
  WHERE c.filename ~ 'uga-irs-lamwo-*'
	AND r.endtime IS NOT NULL) a
LEFT JOIN (
  SELECT r.id, md.dayselapsed,
    CAST(sum(mgd.occurrences) AS INTEGER) AS occurrences,
	CAST(sum(mgd.clinicaloccurrences) AS INTEGER) AS clinicaloccurrences,
	CAST(sum(mgd.weightedoccurrences) AS FLOAT) AS weightedoccurrences
  FROM sim.configuration c
    INNER JOIN sim.replicate r ON r.configurationid = c.id
	INNER JOIN sim.monthlydata md ON md.replicateid = r.id
	INNER JOIN sim.monthlygenomedata mgd ON mgd.monthlydataid = md.id
	INNER JOIN sim.genotype g ON g.id = mgd.genomeid
  WHERE c.filename ~ 'uga-irs-lamwo-*'
    AND r.endtime IS NOT NULL
	AND g.name ~ '^.....Y..'
  GROUP BY r.id, md.dayselapsed) b ON b.id = a.id AND b.dayselapsed = a.dayselapsed
WHERE filename NOT IN ('uga-irs-lamwo.yml', 'uga-irs-lamwo-steady.yml', 'uga-irs-lamwo-steady-zero.yml')
ORDER BY dayselapsed