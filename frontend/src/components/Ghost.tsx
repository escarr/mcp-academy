import type { GhostName } from "../types";

const COLORS: Record<GhostName, string> = {
  blinky: "#FF0000",
  pinky: "#FFB8FF",
  inky: "#00FFFF",
  clyde: "#FFB852",
  pacman: "#FFFF00",
};

interface Props {
  name: GhostName;
  size?: number;
  scared?: boolean;
  className?: string;
}

export function Ghost({ name, size = 48, scared = false, className = "" }: Props) {
  const color = scared ? "#2121FF" : COLORS[name];
  const eyeWhite = scared ? "#FFB8FF" : "#FFFFFF";
  const pupil = scared ? "#FFB8FF" : "#2121FF";

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      className={`ghost-body animate-ghost-bob ${className}`}
      style={{ color }}
    >
      {/* Body */}
      <path
        fill={color}
        d="M16 3 C8 3 4 9 4 16 V28 L7 25 L10 28 L13 25 L16 28 L19 25 L22 28 L25 25 L28 28 V16 C28 9 24 3 16 3 Z"
      />
      {/* Eyes */}
      <circle cx="12" cy="13" r="3.2" fill={eyeWhite} />
      <circle cx="20" cy="13" r="3.2" fill={eyeWhite} />
      <circle cx="13" cy="13" r="1.5" fill={pupil} />
      <circle cx="21" cy="13" r="1.5" fill={pupil} />
      {scared && (
        <>
          <path d="M9 20 L11 18 L13 20 L15 18 L17 20 L19 18 L21 20 L23 18" stroke={eyeWhite} strokeWidth="1" fill="none" />
        </>
      )}
    </svg>
  );
}
