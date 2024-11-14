import { jsx as _jsx } from "react/jsx-runtime";
export const Alert = ({ children, variant = "info", className = "", }) => {
    const variantStyles = {
        info: "bg-blue-100 text-blue-700",
        warning: "bg-yellow-100 text-yellow-700",
        error: "bg-red-100 text-red-700",
        success: "bg-green-100 text-green-700",
    };
    return (_jsx("div", { className: `p-4 rounded ${variantStyles[variant]} ${className}`, children: children }));
};
// Este es el nuevo componente de descripción.
export const AlertDescription = ({ children, }) => _jsx("p", { className: "text-sm mt-2", children: children });
export default Alert;
