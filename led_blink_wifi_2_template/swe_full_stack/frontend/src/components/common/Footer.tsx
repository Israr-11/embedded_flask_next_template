'use client'
import { motion } from "framer-motion";
import { 
  FaFacebookF, 
  FaTwitter, 
  FaInstagram, 
  FaLinkedinIn, 
  FaGithub, 
  FaHeart
} from "react-icons/fa";

export default function Footer() {
  const currentYear = new Date().getFullYear();
  
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.3
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1, transition: { duration: 0.5 } }
  };
  
  const socialLinks = [
    { icon: <FaFacebookF />, url: "/#", label: "Facebook" },
    { icon: <FaTwitter />, url: "/#", label: "Twitter" },
    { icon: <FaInstagram />, url: "/#", label: "Instagram" },
    { icon: <FaLinkedinIn />, url: "/#", label: "LinkedIn" },
    { icon: <FaGithub />, url: "/#", label: "GitHub" }
  ];

  return (
    <footer 
      className="bg-white text-gray-700 relative overflow-hidden border-t border-gray-100 mt-auto"
      style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
    >
      {/* Footer Top - Simplified */}
      <div className="py-6 md:py-8 relative z-10">
        <div className="container mx-auto px-4 md:px-6 lg:px-8">
          <motion.div 
            className="flex flex-col md:flex-row justify-between items-center"
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
          >
            {/* Brand Column */}
            <motion.div variants={itemVariants} className="mb-6 md:mb-0 text-center md:text-left">
              <div className="mb-4">
                <h2 className="text-xl md:text-2xl font-bold text-gray-800 mb-1 flex items-center justify-center md:justify-start">
                  CVEase
                </h2>
                <p className="text-sm md:text-base text-gray-600">Create and Test CVs</p>
              </div>
            </motion.div>
            
            {/* Social Links */}
            <motion.div variants={itemVariants} className="flex gap-2 md:gap-3">
              {socialLinks.map((link, index) => (
                <motion.a 
                  key={index}
                  href={link.url}
                  className="flex items-center justify-center w-8 h-8 md:w-9 md:h-9 rounded-md bg-gray-100 text-gray-700 hover:bg-blue-600 hover:text-white transition-all duration-300"
                  aria-label={link.label}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {link.icon}
                </motion.a>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </div>
      
      {/* Footer Bottom */}
      <div className="bg-blue-600 py-3 text-white">
        <div className="container mx-auto px-4 md:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row md:justify-between md:items-center">
            <p className="text-xs md:text-sm mb-2 md:mb-0 text-center md:text-left">
              &copy; {currentYear} <a href="/" className="font-medium">CVEase</a>. All rights reserved.
            </p>
            <p className="text-xs md:text-sm text-center md:text-right flex items-center justify-center md:justify-end">
              Made with 
              <span className="mx-1 text-red-400">
                <FaHeart />
              </span> 
              by CVEase Team
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}