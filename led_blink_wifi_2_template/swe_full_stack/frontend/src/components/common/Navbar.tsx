'use client'
import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  FaBars, 
  FaTimes, 
  FaPhoneAlt, 
  FaUserPlus
} from "react-icons/fa";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pathname = usePathname();
  
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);
  
  // Close mobile menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (mobileMenuOpen && !target.closest('nav')) {
        setMobileMenuOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [mobileMenuOpen]);
  
  // Close mobile menu when route changes
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);
  
  const handleSignUp = () => {
    alert("Sign up for CVEase");
  };
  
  const handleLinkClick = () => {
    setMobileMenuOpen(false);
  };
  
  const navLinks = [
    { title: "Home", href: "/", active: pathname === '/' },
    { title: "CV", href: "/post", active: pathname === '/post' },
    { title: "ATS", href: "/carousel", active: pathname === '/carousel' },
  ];

  return (
    <header 
      className={`fixed top-0 left-0 w-full z-50 transition-all duration-300 ${
        isScrolled ? 'bg-white shadow-md py-2' : 'bg-gray-50 py-3'
      }`}
      style={{ paddingTop: 'env(safe-area-inset-top)' }}
    >
      <div className="container-fluid max-w-[1520px] mx-auto">
        <nav className="flex items-center justify-between mx-auto px-4 md:px-8 lg:px-12">
          <Link 
            href="/"
            className="flex items-center text-decoration-none"
            onClick={handleLinkClick}
          >
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="flex items-center"
            >
              <span className="text-xl xs:text-2xl font-bold text-gray-800 tracking-wide">CVEase</span>
            </motion.div>
          </Link>
          
          <motion.div 
            className="hidden lg:flex items-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
          >
            <ul className="flex">
              {navLinks.map((link, index) => (
                <motion.li 
                  key={index}
                  className="relative mx-3"
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * (index + 1), duration: 0.5 }}
                >
                  <Link 
                    href={link.href} 
                    className={`block px-4 py-2 font-medium transition-colors duration-300 ${
                      link.active ? 'text-blue-600' : 'text-gray-600 hover:text-blue-600'
                    }`}
                    onClick={handleLinkClick}
                  >
                    {link.title}
                    {link.active && (
                      <span className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-1.5 h-1.5 bg-blue-600 rounded-full"></span>
                    )}
                  </Link>
                </motion.li>
              ))}
            </ul>
            
            <motion.button 
              className="ml-8 bg-blue-600 text-white font-medium py-2 px-6 rounded-md flex items-center gap-2 hover:bg-blue-700 transition-all duration-300"
              onClick={handleSignUp}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.5 }}
            >
              <FaUserPlus className="text-sm" />
              <span>Sign Up</span>
            </motion.button>
          </motion.div>
          
          <motion.button 
            className="block lg:hidden text-gray-700 text-xl p-2 focus:outline-none"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <FaTimes /> : <FaBars />}
          </motion.button>
        </nav>
      </div>
      
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div 
            className="lg:hidden bg-white shadow-lg fixed top-[calc(3.5rem+env(safe-area-inset-top))] left-0 right-0 z-40 max-h-[calc(100vh-3.5rem-env(safe-area-inset-top))] overflow-auto"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            <div className="container mx-auto px-4 py-4">
              <ul className="mb-5">
                {navLinks.map((link, index) => (
                  <motion.li 
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.05 * index, duration: 0.3 }}
                  >
                    <Link 
                      href={link.href} 
                      className={`block py-4 font-medium border-b border-gray-100 ${
                        link.active ? 'text-blue-600' : 'text-gray-600'
                      }`}
                      onClick={handleLinkClick}
                    >
                      {link.title}
                    </Link>
                  </motion.li>
                ))}
              </ul>
              
              <motion.div 
                className="flex flex-col gap-3"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3, duration: 0.3 }}
              >
                <button 
                  className="bg-blue-600 text-white font-medium py-3 px-5 rounded flex items-center justify-center gap-2 hover:bg-blue-700 transition-all duration-300"
                  onClick={handleSignUp}
                >
                  <FaUserPlus className="text-sm" />
                  <span>Sign Up</span>
                </button>
                
                <a 
                  href="tel:+11121211111" 
                  className="flex items-center justify-center gap-2 py-3 px-5 border border-gray-200 rounded text-gray-600 font-medium hover:bg-gray-50 transition-all duration-300"
                >
                  <FaPhoneAlt className="text-sm" />
                  <span>+1-112-121-1111</span>
                </a>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}