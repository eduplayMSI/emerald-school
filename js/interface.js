// js/interface.js — tolerante a elementos ausentes
export function setProgress(p) {
  const fill = document.getElementById('progress-fill');
  const txt  = document.getElementById('progress-text');
  const pct  = Math.max(0, Math.min(1, p)) * 100;
  if (fill) fill.style.width = pct.toFixed(0) + '%';
  if (txt)  txt.textContent = `Carregando… ${pct.toFixed(0)}%`;
}
export function showStartButton(onStart) {
  const btn = document.getElementById('start-btn');
  if (!btn) return;
  btn.style.display = 'block';
  btn.onclick = () => onStart();
}
export function hideLoading() {
  const el = document.getElementById('loading');
  if (el) el.style.display = 'none';
}
export function showControlsInfo() {
  const el = document.getElementById('controls-info');
  if (el) el.style.display = 'block';
}
export function hideControlsInfo() {
  const el = document.getElementById('controls-info');
  if (el) el.style.display = 'none';
}
export function showError(msg) {
  hideLoading();
  const el = document.getElementById('error');
  if (el) { el.textContent = '⚠ ' + msg; el.style.display = 'block'; }
}