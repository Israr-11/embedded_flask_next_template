import Image from "next/image";
import Link from "next/link";
import Navbar from "@/components/common/Navbar";
import Footer from "@/components/common/Footer";
import { FaBriefcase, FaChartBar } from "react-icons/fa";

export default function Home() {
  return (
    <main className="overflow-x-hidden min-h-screen flex flex-col">
      <Navbar />
      <Footer />
    </main>
  );
}
