import { jsx as _jsx } from "react/jsx-runtime";
import './Table.module.css';
export const Table = ({ children }) => {
    return _jsx("table", { className: "table", children: children });
};
export const TableBody = ({ children }) => {
    return _jsx("tbody", { children: children });
};
export const TableCell = ({ children }) => {
    return _jsx("td", { className: "table-cell", children: children });
};
export const TableHead = ({ children }) => {
    return _jsx("thead", { children: children });
};
export const TableHeader = ({ children }) => {
    return _jsx("th", { className: "table-header", children: children });
};
export const TableRow = ({ children }) => {
    return _jsx("tr", { className: "table-row", children: children });
};
