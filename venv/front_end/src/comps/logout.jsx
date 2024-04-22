// components/Logout.js
import React, { useEffect } from 'react';

function Logout() {
  useEffect(() => {
    // Send logout request to backend
    const logout = async () => {
      try {
        const response = await fetch('/logout');
        const data = await response.json();
        console.log(data);
      } catch (error) {
        console.error('Error:', error);
      }
    };

    logout();
  }, []);

  return (
    <div>
      <h2>Logging out...</h2>
    </div>
  );
}

export default Logout;
