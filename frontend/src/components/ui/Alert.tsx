// frontend/src/components/ui/Alert.tsx
import React from 'react';

interface AlertProps {
  children: React.ReactNode;
  variant?: 'info' | 'warning' | 'error' | 'success';
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({ children, variant = 'info', className = '' }) => {
  const variantStyles = {
    info: 'bg-blue-100 text-blue-700',
    warning: 'bg-yellow-100 text-yellow-700',
    error: 'bg-red-100 text-red-700',
    success: 'bg-green-100 text-green-700',
  };

  return (
    <div className={`p-4 rounded ${variantStyles[variant]} ${className}`}>
      {children}
    </div>
  );
};

// Este es el nuevo componente de descripción.
export const AlertDescription: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <p className="text-sm mt-2">
    {children}
  </p>
);

export default Alert;
