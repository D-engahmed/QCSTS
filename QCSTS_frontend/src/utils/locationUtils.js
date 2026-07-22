// ─── LOCATION UTILITIES ──────────────────────────────────────
import { db } from "../data/db.js";

export let locationTargetBatchId = null;

export function getBatch(batchId) {
  return db.batches.find((b) => b.id === batchId);
}

export function getProduct(productId) {
  return db.products.find((p) => p.id === productId);
}

export function isLocationTaken(shelf, rack, pos, excludeBatchId) {
  return db.batches.some(b => 
    b.id !== excludeBatchId && 
    b.shelf === shelf && 
    b.rack === rack && 
    b.position === pos
  );
}

export function confirmLocationChange(newShelf, newRack, newPosition, reason) {
  const shelf = newShelf.trim().toUpperCase();
  const rack = newRack.trim().toUpperCase();
  const pos = newPosition.trim().toUpperCase();
  const reasonText = reason.trim();
  
  if (!shelf || !rack || !pos || !reasonText) {
    console.error('Fill all fields');
    return false;
  }
  
  if (isLocationTaken(shelf, rack, pos, locationTargetBatchId)) {
    console.error('Location already taken');
    return false;
  }
  
  const b = getBatch(locationTargetBatchId);
  
  // Log movement
  db.locationHistory.push({
    batchId: b.id,
    batchNo: b.batchNo,
    fromShelf: b.shelf,
    fromRack: b.rack,
    fromPos: b.position,
    toShelf: shelf,
    toRack: rack,
    toPos: pos,
    date: new Date().toISOString().split('T')[0],
    reason: reasonText
  });
  
  b.shelf = shelf;
  b.rack = rack;
  b.position = pos;
  
  console.log(`📍 Location updated → ${shelf}/${rack}/${pos}`);
  return true;
}

export function showLocationHistory(batchId) {
  const b = getBatch(batchId);
  const prod = getProduct(b.productId);
  const history = db.locationHistory.filter(h => h.batchId === batchId);
  
  console.log('Location history for:', prod.name, b.batchNo);
  console.log('Current location:', `${b.shelf}/${b.rack}/${b.position}`);
  console.log('History:', history);
  return { batch: b, product: prod, history };
}

export function showChangeLocation(batchId) {
  locationTargetBatchId = batchId;
  const b = getBatch(batchId);
  const prod = getProduct(b.productId);
  console.log('Show change location for:', prod.name, b.batchNo);
  return { batch: b, product: prod };
}

export function formatDate(dateStr) {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleDateString();
}
