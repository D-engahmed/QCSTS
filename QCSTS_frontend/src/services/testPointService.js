import { db, LONG_MONTHS, ACCEL_MONTHS } from "../data/db";

export function generateTestPoints(batch){
  if (!batch || !batch.mfgDate) return;
  
  const months = batch.studyType === "Long Study" ? LONG_MONTHS : ACCEL_MONTHS;
  
  // Try to get a valid base date
  let base;
  if (batch.incubationDate) {
    base = new Date(batch.incubationDate);
  } else if (batch.mfgDate) {
    base = new Date(batch.mfgDate);
  } else {
    return;
  }
  
  // Check if base date is valid
  if (isNaN(base.getTime())) return;

  months.forEach(m => {
    const d = new Date(base);
    d.setMonth(d.getMonth() + m);
    
    // Check if calculated date is valid
    if (!isNaN(d.getTime())) {
      db.testPoints.push({
        id: db.nextId.testPoint++,
        batchId: batch.id,
        month: m,
        label: m === 0 ? "Initial" : `${m}M`,
        scheduledDate: d.toISOString().split("T")[0],
        status: "Pending"
      });
    }
  });
}