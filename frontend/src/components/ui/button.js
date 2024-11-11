import { jsx as _jsx } from "react/jsx-runtime";
import styles from './Button.module.css';
export const Button = ({ children, onClick, variant = 'primary', size, className = '' }) => {
    const variantStyle = variant ? styles[variant] : styles.primary;
    const sizeStyle = size ? styles[size] : '';
    return (_jsx("button", { className: `${styles.baseStyle} ${variantStyle} ${sizeStyle} ${className}`, onClick: onClick, children: children }));
};
export default Button;
