import Link from "next/link";
import { Cloud } from "lucide-react";

export function Brand({ inverse = false }: { inverse?: boolean }) {
  return (
    <Link href="/" className={`brand${inverse ? " brand-inverse" : ""}`} aria-label="Cloudheo">
      <span className="brand-mark"><Cloud size={21} strokeWidth={1.8} aria-hidden="true" /></span>
      <span>cloudheo<span className="brand-period">.</span></span>
    </Link>
  );
}