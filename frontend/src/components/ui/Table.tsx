// src/components/ui/Table.tsx
import React from "react";
import "./Table.module.css";

export const Table = ({ children }: { children: React.ReactNode }) => {
  return <table className="table">{children}</table>;
};

export const TableBody = ({ children }: { children: React.ReactNode }) => {
  return <tbody>{children}</tbody>;
};

export const TableCell = ({ children }: { children: React.ReactNode }) => {
  return <td className="table-cell">{children}</td>;
};

export const TableHead = ({ children }: { children: React.ReactNode }) => {
  return <thead>{children}</thead>;
};

export const TableHeader = ({ children }: { children: React.ReactNode }) => {
  return <th className="table-header">{children}</th>;
};

export const TableRow = ({ children }: { children: React.ReactNode }) => {
  return <tr className="table-row">{children}</tr>;
};
