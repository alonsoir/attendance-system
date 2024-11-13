// frontend/src/components/ui/Button.tsx
import React from "react";
import styles from "./Button.module.css";

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: "primary" | "secondary" | "ghost";
  size?: "small" | "icon";
  className?: string;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  variant = "primary",
  size,
  className = "",
}) => {
  const variantStyle = variant ? styles[variant] : styles.primary;
  const sizeStyle = size ? styles[size] : "";

  return (
    <button
      className={`${styles.baseStyle} ${variantStyle} ${sizeStyle} ${className}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
};

export default Button;
