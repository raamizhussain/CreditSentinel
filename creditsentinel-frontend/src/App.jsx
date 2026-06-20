import React, { useState } from 'react';
import { ShieldAlert, ShieldCheck, Activity, User, DollarSign, Percent, AlertCircle } from 'lucide-react';

function App() {
  const [formData, setFormData] = useState({
    applicant_name: '',
    credit_score: 700,
    monthly_debt: 1500,
    monthly_income: 5000,
    outstanding_balance_current: 8000,
    outstanding_balance_prior: 7500,
    late_payments_30d: 0,
    late_payments_60d: 0,
    late_payments_90d: 0,
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'applicant_name' ? value : Number(value)
    });
  };

  const handleEvaluate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://127.0.0.1:8000/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, risk_label: 'LOW' }),
      });
      if (!response.ok) throw new Error('Failed to fetch prediction from API engine.');
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', backgroundColor: '#f3f4f6', minHeight: '100vh', padding: '2rem' }}>
      <header style={{ maxWidth: '1200px', margin: '0 auto 2rem auto', display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <Activity size={32} color="#2563eb" />
        <h1 style={{ margin: 0, fontSize: '1.875rem', color: '#111827' }}>CreditSentinel <span style={{ fontWeight: 300, color: '#6b7280' }}>| Underwriting Portal</span></h1>
      </header>

      <main style={{ maxWidth: '1200px', margin: '0 auto', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        {/* Left Side: Loan Application Form */}
        <div style={{ backgroundColor: '#ffffff', padding: '2rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h2 style={{ marginTop: 0, fontSize: '1.25rem', marginBottom: '1.5rem', color: '#374151' }}>Applicant Profile Data</h2>
          <form onSubmit={handleEvaluate} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}><User size={14} /> Full Name</label>
              <input type="text" name="applicant_name" required value={formData.applicant_name} onChange={handleInputChange} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #d1d5db' }} />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}>Credit Score (300-850)</label>
                <input type="number" name="credit_score" min="300" max="850" value={formData.credit_score} onChange={handleInputChange} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #d1d5db' }} />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}><DollarSign size={14} /> Monthly Income ($)</label>
                <input type="number" name="monthly_income" value={formData.monthly_income} onChange={handleInputChange} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #d1d5db' }} />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}><DollarSign size={14} /> Monthly Debt ($)</label>
                <input type="number" name="monthly_debt" value={formData.monthly_debt} onChange={handleInputChange} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #d1d5db' }} />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}><DollarSign size={14} /> Current Balance ($)</label>
                <input type="number" name="outstanding_balance_current" value={formData.outstanding_balance_current} onChange={handleInputChange} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #d1d5db' }} />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}><DollarSign size={14} /> Previous Balance ($)</label>
                <input type="number" name="outstanding_balance_prior" value={formData.outstanding_balance_prior} onChange={handleInputChange} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #d1d5db' }} />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}>30d Late Logs</label>
                <input type="number" name="late_payments_30d" value={formData.late_payments_30d} onChange={handleInputChange} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #d1d5db' }} />
              </div>
            </div>

            <button type="submit" disabled={loading} style={{ backgroundColor: '#2563eb', color: '#ffffff', border: 'none', padding: '0.75rem', borderRadius: '4px', fontWeight: 600, cursor: 'pointer', marginTop: '1rem' }}>
              {loading ? 'Evaluating Risk Matrices...' : 'Evaluate Application'}
            </button>
          </form>
        </div>

        {/* Right Side: Real-Time Results & Explanations */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {error && (
            <div style={{ backgroundColor: '#fee2e2', color: '#991b1b', padding: '1rem', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertCircle size={20} />
              <span>{error}</span>
            </div>
          )}

          {!result && !error && (
            <div style={{ border: '2px dashed #d1d5db', borderRadius: '8px', height: '100%', display: 'flex', alignItems: 'center', justify_content: 'center', color: '#6b7280' }}>
              Enter applicant metrics and click evaluate to parse compliance analytics.
            </div>
          )}

          {result && (
            <div style={{ backgroundColor: '#ffffff', padding: '2rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justify_content: 'space-between', marginBottom: '1.5rem' }}>
                <h3 style={{ margin: 0, fontSize: '1.25rem', color: '#374151' }}>Automated Risk Decision</h3>
                {result.final_risk_probability > 0.5 ? (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', backgroundColor: '#fee2e2', color: '#991b1b', padding: '0.25rem 0.75rem', borderRadius: '9999px', fontWeight: 600, fontSize: '0.875rem' }}><ShieldAlert size={16} /> REJECTED</span>
                ) : (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', backgroundColor: '#dcfce7', color: '#166534', padding: '0.25rem 0.75rem', borderRadius: '9999px', fontWeight: 600, fontSize: '0.875rem' }}><ShieldCheck size={16} /> APPROVED</span>
                )}
              </div>

              <div style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', justify_content: 'space-between', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}>
                  <span>Empirical Default Probability</span>
                  <span>{(result.final_risk_probability * 100).toFixed(2)}%</span>
                </div>
                <div style={{ backgroundColor: '#e5e7eb', borderRadius: '9999px', height: '12px', overflow: 'hidden' }}>
                  <div style={{ backgroundColor: result.final_risk_probability > 0.5 ? '#dc2626' : '#16a34a', height: '100%', width: `${result.final_risk_probability * 100}%`, transition: 'width 0.3s ease' }}></div>
                </div>
              </div>

              <div>
                <h4 style={{ margin: '0 0 1rem 0', fontSize: '1rem', color: '#374151' }}>Adverse Action Compliance Drivers (SHAP Absolute Attribution)</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {result.top_decision_drivers.map((driver, idx) => (
                    <div key={idx} style={{ borderLeft: `4px solid ${driver.shap_value > 0 ? '#dc2626' : '#16a34a'}`, paddingLeft: '1rem', paddingY: '0.25rem' }}>
                      <div style={{ display: 'flex', justify_content: 'space-between', fontSize: '0.875rem' }}>
                        <span style={{ fontWeight: 600, color: '#4b5563' }}>{driver.feature}</span>
                        <span style={{ color: driver.shap_value > 0 ? '#dc2626' : '#16a34a', fontWeight: 500 }}>
                          {driver.shap_value > 0 ? '+' : ''}{driver.shap_value.toFixed(4)} Impact
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;