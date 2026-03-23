import { motion } from "framer-motion";

function AIOrb({ toggleAssistant }) {

  return (
    <motion.div
      onClick={toggleAssistant}
      className="fixed bottom-6 right-6 w-16 h-16 rounded-full cursor-pointer flex items-center justify-center"
      animate={{ scale: [1, 1.15, 1] }}
      transition={{ duration: 2, repeat: Infinity }}
      style={{
        background: "radial-gradient(circle at 30% 30%, #60a5fa, #9333ea)",
        boxShadow:
          "0 0 20px rgba(99,102,241,0.7), 0 0 40px rgba(147,51,234,0.5)"
      }}
    >
      🤖
    </motion.div>
  );
}

export default AIOrb;