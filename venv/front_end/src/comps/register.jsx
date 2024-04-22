import React, { useState } from 'react';

function Register() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '', // Corrected field name
    phone_number: '',
    address: '',
    is_superuser: '', // Assuming this is a boolean field
    date_of_birth: '' // Assuming this is a date field
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Client-side form validation
    if (!formData.username || !formData.email || !formData.password) {
      setError('Please fill in all required fields.');
      return;
    }
    // Send registration request to backend
    try {
      const response = await fetch('http://localhost:8000/register', {
        method: 'POST',
        mode:'cors',
        cache:'no-cache',
        credentials:'same-origin',
        headers: {
          'Content-Type': 'application/json'
        },
        redirect:'follow',
        referrerPolicy:'no-referrer',
        body: JSON.stringify({
          ...formData,
          password_hash: formData.password // Rename password to password_hash
        })
      });
      const data = await response.json();
      if (response.ok) {
        setSuccess(true);
        setError('');
        // Clear form fields
        setFormData({
          username: '',
          email: '',
          password: '',
          full_name: '', // Reset to empty string
          phone_number: '',
          address: '',
          is_superuser: '',
          date_of_birth: ''
        });
      } else {
        setError(data.message || 'Registration failed. Please try again later.');
      }
    } catch (error) {
      console.error('Error:', error);
      setError('An unexpected error occurred. Please try again later.');
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div>
      <h2>Register</h2>
      {success && <p>Registration successful. You can now login.</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input type="text" name="username" placeholder="Username" value={formData.username} onChange={handleChange} />
        <input type="email" name="email" placeholder="Email" value={formData.email} onChange={handleChange} />
        <input type="password" name="password" placeholder="Password" value={formData.password} onChange={handleChange} />
        <input type="text" name="full_name" placeholder="Full Name" value={formData.full_name} onChange={handleChange} /> {/* Corrected field name */}
        <input type="tel" name="phone_number" placeholder="Phone Number" value={formData.phone_number} onChange={handleChange} />
        <input type="text" name="address" placeholder="Address" value={formData.address} onChange={handleChange} />
        <input type="text" name="is_superuser" placeholder="Admin?" value={formData.is_superuser} onChange={handleChange} />
        <input type="date" name="date_of_birth" placeholder="Date of Birth" value={formData.date_of_birth} onChange={handleChange} />
        <button type="submit">Register</button>
      </form>
    </div>
  );
}

export default Register;
  // Send registration request to backend

