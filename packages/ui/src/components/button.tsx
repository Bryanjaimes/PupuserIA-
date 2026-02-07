import React from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: (string | undefined | null | boolean)[]) {
  return twMerge(clsx(inputs));
}

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "impact";
  size?: "sm" | "md" | "lg";
  children: React.ReactNode;
}

export function Button({
  variant = "primary",
  size = "md",
  className,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-xl font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2",
        // Variants
        variant === "primary" &&
          "bg-primary-700 text-white hover:bg-primary-800 focus:ring-primary-500",
        variant === "secondary" &&
          "bg-gold-500 text-primary-950 hover:bg-gold-400 focus:ring-gold-500",
        variant === "outline" &&
          "border-2 border-primary-700 text-primary-700 hover:bg-primary-50 focus:ring-primary-500",
        variant === "ghost" &&
          "text-primary-700 hover:bg-primary-50 focus:ring-primary-500",
        variant === "impact" &&
          "bg-impact-500 text-white hover:bg-impact-600 focus:ring-impact-500",
        // Sizes
        size === "sm" && "px-4 py-2 text-sm",
        size === "md" && "px-6 py-3 text-base",
        size === "lg" && "px-8 py-4 text-lg",
        className,
      )}
      {...props}
    >
      {children}
    </button>
  );
}
