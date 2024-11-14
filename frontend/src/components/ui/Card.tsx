import React from "react";
import styles from "./Card.module.css";

interface CardProps {
 children: React.ReactNode;
 className?: string;
 shadow?: boolean;
 rounded?: boolean;
}

export const Card: React.FC<CardProps> = ({
 children,
 className = "",
 shadow = true,
 rounded = false,
}) => {
 const shadowStyle = shadow ? styles.shadow : styles.noShadow;
 const roundedStyle = rounded ? styles.rounded : "";

 return (
   <div className={`${styles.baseStyle} ${shadowStyle} ${roundedStyle} ${className}`}>
     {children}
   </div>
 );
};

export const CardHeader: React.FC<CardProps> = ({
 children,
 className = "",
}) => (
 <div className={`${styles.cardHeader} ${className}`}>
   {children}
 </div>
);

export const CardTitle: React.FC<CardProps> = ({
 children,
 className = "",
}) => (
 <h3 className={`${styles.cardTitle} ${className}`}>
   {children}
 </h3>
);

export const CardContent: React.FC<CardProps> = ({
 children,
 className = "",
}) => (
 <div className={`${styles.cardContent} ${className}`}>
   {children}
 </div>
);