import React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "accent" | "dark" | "outline";
  size?: "sm" | "md" | "lg";
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "primary",
  size = "md",
  className = "",
  ...props
}) => {
  const baseStyles =
    "inline-flex items-center justify-center font-bold uppercase tracking-wider transition-colors select-none rounded-none disabled:opacity-50 disabled:cursor-not-allowed";

  const sizeStyles = {
    sm: "px-3 py-1.5 text-xs",
    md: "px-5 py-2.5 text-xs",
    lg: "px-6 py-3.5 text-sm",
  };

  const variantStyles = {
    primary: "bg-electric-blue text-pure-white hover:bg-blue-700",
    accent: "bg-acid-lime text-carbon-pitch hover:bg-lime-400",
    dark: "bg-carbon-pitch text-pure-white hover:bg-zinc-800",
    outline:
      "bg-pure-white text-carbon-pitch border border-hairline-border hover:border-carbon-pitch",
  };

  return (
    <button
      className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};
