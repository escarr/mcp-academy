interface Props {
  size?: number;
  chomping?: boolean;
  className?: string;
  facing?: "right" | "left" | "up" | "down";
}

export function Pacman({ size = 48, chomping = true, className = "", facing = "right" }: Props) {
  const rotate = { right: 0, down: 90, left: 180, up: 270 }[facing];
  return (
    <div
      style={{ width: size, height: size, transform: `rotate(${rotate}deg)` }}
      className={className}
    >
      <div
        className={chomping ? "animate-chomp pacman-mouth" : "pacman-mouth"}
        style={{
          width: "100%",
          height: "100%",
          borderRadius: "50%",
        }}
      />
    </div>
  );
}

export function Pellet({ size = 8, power = false }: { size?: number; power?: boolean }) {
  const s = power ? size * 2 : size;
  return (
    <div
      style={{
        width: s,
        height: s,
        borderRadius: "50%",
        background: "#FFB897",
        boxShadow: "0 0 6px #FFB897, 0 0 14px rgba(255,184,151,0.6)",
        display: "inline-block",
      }}
      className={power ? "animate-float" : ""}
    />
  );
}
