import React from "react";
import styles from "./Table.module.css";

export interface TableProps {
  children: React.ReactNode;
  className?: string;
}

export const Table: React.FC<TableProps> = ({ children, className = "" }) => {
  return <table className={`${styles.table} ${className}`}>{children}</table>;
};

export const TableHeader: React.FC<TableProps> = ({
  children,
  className = "",
}) => {
  return (
    <thead className={`${styles.tableHeader} ${className}`}>{children}</thead>
  );
};

export const TableBody: React.FC<TableProps> = ({
  children,
  className = "",
}) => {
  return (
    <tbody className={`${styles.tableBody} ${className}`}>{children}</tbody>
  );
};

export const TableRow: React.FC<TableProps> = ({
  children,
  className = "",
}) => {
  return <tr className={`${styles.tableRow} ${className}`}>{children}</tr>;
};

export const TableCell: React.FC<TableProps> = ({
  children,
  className = "",
}) => {
  return <td className={`${styles.tableCell} ${className}`}>{children}</td>;
};

export const TableHead: React.FC<TableProps> = ({
  children,
  className = "",
}) => {
  return <th className={`${styles.tableHead} ${className}`}>{children}</th>;
};

export { Table as default };
