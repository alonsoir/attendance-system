import { jsx as _jsx } from "react/jsx-runtime";
import styles from "./Card.module.css";
export const Card = ({ children, className = "", shadow = true, rounded = false, }) => {
    const shadowStyle = shadow ? styles.shadow : styles.noShadow;
    const roundedStyle = rounded ? styles.rounded : "";
    return (_jsx("div", { className: `${styles.baseStyle} ${shadowStyle} ${roundedStyle} ${className}`, children: children }));
};
export default Card;
