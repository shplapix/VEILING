import React from "react";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "lime" | "blue" | "carbon" | "neutral";
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "lime",
  className = "",
}) => {
  const baseStyles =
    "inline-flex items-center px-2 py-0.5 text-[10px] font-mono font-bold tracking-kicker uppercase rounded-none";

  const variantStyles = {
    lime: "bg-acid-lime text-carbon-pitch",
    blue: "bg-electric-blue text-pure-white",
    carbon: "bg-carbon-pitch text-pure-white",
    neutral: "bg-gallery-canvas text-carbon-pitch border border-hairline-border",
  };

  return (
    <span className={`${baseStyles} ${variantStyles[variant]} ${className}`}>
      {children}
    </span>
  );
};
