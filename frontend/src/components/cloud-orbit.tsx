import { Cloud, Database, HardDrive, Server } from "lucide-react";

/** A decorative, CSS-only cloud illustration. No canvas or animation loop. */
export function CloudOrbit() {
  return (
    <div className="cloud-orbit" aria-hidden="true">
      <div className="orbit-ring orbit-ring-one" />
      <div className="orbit-ring orbit-ring-two" />
      <div className="orbit-ring orbit-ring-three" />
      <div className="orbit-core"><Cloud size={48} strokeWidth={1.2} /></div>
      <span className="orbit-node orbit-node-one"><Server size={22} strokeWidth={1.5} /></span>
      <span className="orbit-node orbit-node-two"><Database size={22} strokeWidth={1.5} /></span>
      <span className="orbit-node orbit-node-three"><HardDrive size={22} strokeWidth={1.5} /></span>
      <span className="orbit-point orbit-point-one" />
      <span className="orbit-point orbit-point-two" />
    </div>
  );
}