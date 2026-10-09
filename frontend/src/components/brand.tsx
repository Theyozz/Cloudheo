import Link from "next/link";
import Image from "next/image";

export function Brand({ inverse = false }: { inverse?: boolean }) {
  return (
    <Link href="/" className={`brand${inverse ? " brand-inverse" : ""}`} aria-label="Cloudheo">
      <span className="brand-mark">
        <Image src="/logo-mark.png" alt="" width={240} height={164} priority aria-hidden="true" />
      </span>
      <span>cloudheo<span className="brand-period">.</span></span>
    </Link>
  );
}