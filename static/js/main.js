// flask_app/static/js/main.js
async function predict() {
  const fields = ['age','gender','height','weight',
                   'ap_hi','ap_lo','cholesterol','gluc',
                   'smoke','alco','active'];
  const data = {};
  for (const f of fields) {
    const val = document.getElementById(f).value;
    if (!val) { alert('Please fill all fields!'); return; }
    data[f] = val;
  }
  const btn = document.querySelector('.btn-predict');
  btn.textContent = 'Analysing...'; btn.disabled = true;
  try {
    const res  = await fetch('/predict', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    });
    const json = await res.json();
    displayResult(json);
  } catch(e) {
    alert('Prediction failed: ' + e.message);
  } finally {
    btn.textContent = 'Classify Blood Pressure'; btn.disabled = false;
  }
}
 
function displayResult(data) {
  const card = document.getElementById('result-card');
  card.classList.remove('hidden');
  const cls  = data.prediction <= 0 ? 'normal' :
               data.prediction == 1 ? 'elevated' : 'high';
  let probHTML = '';
  for (const [label, pct] of Object.entries(data.probabilities)) {
    probHTML += `<p>${label}: <b>${pct}%</b></p>
      <div class="progress-bar-wrap">
        <div class="progress-bar" style="width:${pct}%"></div>
      </div>`;
  }
  card.innerHTML = `
    <h3 class="result-label result-${cls}">${data.label}</h3>
    <p><b>Confidence:</b> ${data.confidence}%  BMI: ${data.bmi}</p>
    <hr style="margin:1rem 0">
    <h4>Class Probabilities</h4>${probHTML}
    <hr style="margin:1rem 0">
    <p><b>Advice:</b> ${data.advice}</p>
  `;
  card.scrollIntoView({behavior:'smooth'});
}
