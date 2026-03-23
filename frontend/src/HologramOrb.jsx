import { Canvas } from "@react-three/fiber";
import { Float, MeshDistortMaterial } from "@react-three/drei";
import { motion } from "framer-motion";

function Orb() {
  return (
    <Float speed={2} rotationIntensity={1} floatIntensity={2}>
      <mesh>
        <sphereGeometry args={[1, 64, 64]} />
        <MeshDistortMaterial
          color="#7c3aed"
          attach="material"
          distort={0.4}
          speed={2}
          roughness={0}
        />
      </mesh>
    </Float>
  );
}

function HologramOrb({ toggleAssistant }) {
  return (
    <motion.div
      onClick={toggleAssistant}
      className="fixed bottom-6 right-6 w-24 h-24 cursor-pointer"
      animate={{ scale: [1, 1.1, 1] }}
      transition={{ duration: 3, repeat: Infinity }}
    >
      <Canvas>
        <ambientLight intensity={1} />
        <directionalLight position={[3, 3, 3]} />
        <Orb />
      </Canvas>
    </motion.div>
  );
}

export default HologramOrb;